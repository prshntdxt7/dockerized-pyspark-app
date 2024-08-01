import argparse
import json
import os
import datetime
import math
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

# Constants
MIN_RES = 160000
MAX_RES = 2073600
MIN_AR = 0.3
MAX_AR = 4.65
MAX_FRESHNESS_DAYS = 10 * 365
WEIGHT_RESOLUTION = 6
WEIGHT_ASPECT_RATIO = 2
WEIGHT_FRESHNESS = 2
WEIGHT_TAG_PRIORITY = 3


def calculate_scores(images, tags):
    today = datetime.datetime.now()

    for image in images:
        width = image.get('width', 0)
        height = image.get('height', 0)
        created_date = datetime.datetime.strptime(image.get('created_at'), '%Y-%m-%d')
        image_tags = [tag.get('tag') for tag in image.get('tags', [])]

        # Prepare features
        resolution = width * height
        aspect_ratio = width / height if height != 0 else None
        freshness = (today - created_date).days

        # Calculate resolution score
        if resolution <= 0:
            score_res = 0
        else:
            score_res = (math.log(resolution) - math.log(MIN_RES)) / (math.log(MAX_RES) - math.log(MIN_RES))
            score_res = min(score_res, 1)

        # Calculate aspect ratio score
        if aspect_ratio is None:
            score_ar = 0
        else:
            score_ar = max(0, min(1, (aspect_ratio - MIN_AR) / (MAX_AR - MIN_AR)))

        # Calculate freshness score
        score_fresh = 1 + (-1 * freshness / MAX_FRESHNESS_DAYS)
        score_fresh = max(0, min(score_fresh, 1))

        # Calculate tag priority score
        score_tag = max([tags.get(tag, 0) for tag in image_tags] or [0])

        # Calculate overall score
        score_image = (
                              WEIGHT_RESOLUTION * score_res +
                              WEIGHT_ASPECT_RATIO * score_ar +
                              WEIGHT_FRESHNESS * score_fresh +
                              WEIGHT_TAG_PRIORITY * score_tag
                      ) / (
                              WEIGHT_RESOLUTION + WEIGHT_ASPECT_RATIO +
                              WEIGHT_FRESHNESS + WEIGHT_TAG_PRIORITY
                      )

        image['score'] = score_image

    return images


def main(images_path, tags_path, main_images_path, output_cdc_path, output_snapshot_path, output_metrics_path):
    spark = SparkSession.builder.appName("ImageSelection").getOrCreate()

    # Read input files
    images_df = spark.read.json(images_path)
    tags_df = spark.read.json(tags_path)
    main_images_df = spark.read.json(main_images_path)

    # Flatten tags data
    tags_df = tags_df.withColumn("tag", explode(col("tags.tag")))
    tags_df_pandas = tags_df.toPandas()

    print("Images DataFrame:")
    print(images_df.show(10, False))

    print("Tags DataFrame:")
    print(tags_df.show(10, False))

    print("Main Images DataFrame:")
    print(main_images_df.show(10, False))

    # Images processing
    images = images_df.toPandas().to_dict(orient='records')

    # Check for duplicates
    if 'tag' in tags_df_pandas.columns:
        tags_df_pandas = tags_df_pandas.drop_duplicates(subset=['tag'])
    else:
        print("Error: 'tag' column is missing in tags DataFrame")
        return

    # Create tags dictionary
    tags = tags_df_pandas.set_index('tag').to_dict(orient='index')

    # Handle empty DataFrames
    if not images:
        print("Error: No images data found")
        return

    if not tags:
        print("Error: No tags data found")
        return

    main_images = main_images_df.toPandas().to_dict(orient='records')

    # Process images
    processed_images = calculate_scores(images, tags)

    # Writing output files
    with open(output_cdc_path, 'w') as f:
        json.dump(processed_images, f)

    with open(output_snapshot_path, 'w') as f:
        json.dump(processed_images, f)

    metrics = {
        "total_images": len(images),
        "processed_images": len(processed_images),
        "main_images_selected": len([img for img in processed_images if img['score'] > 0])
    }

    with open(output_metrics_path, 'w') as f:
        json.dump(metrics, f)

    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Main Image Selection')
    parser.add_argument('--images', required=True, help='Local filesystem path to the JSONL file containing the images.')
    parser.add_argument('--tags', required=True, help='Local filesystem path to the JSONL file containing the image tags.')
    parser.add_argument('--main_images', required=True, help='Local filesystem path to the JSONL file containing the existing main images.')
    parser.add_argument('--output_cdc', required=True, help='Local filesystem path to write JSONL file(s) containing the changes.')
    parser.add_argument('--output_snapshot', required=True, help='Local filesystem path to write JSONL file(s) containing the snapshot of the pipeline run.')
    parser.add_argument('--output_metrics', required=True, help='Local filesystem path to a single JSONL file to write the metrics of the pipeline.')

    args = parser.parse_args()
    main(args.images, args.tags, args.main_images, args.output_cdc, args.output_snapshot, args.output_metrics)
    print("Script Execution Completed | Exit 0")
    exit(0)