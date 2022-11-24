import boto3
import re
import argparse

config = None
regex = None
dry_run = False
client = boto3.client('ecr', region_name='us-east-1')

def get_all_images_from_ecr():
    """  
        Description: Get all images id of specific repo in registry
        OUTPUT: list of images id of repo and registry (sent as arguments)
    """

    results = (
        client.get_paginator('list_images')
            .paginate(
            **config,
            maxResults=1000,
            filter={
                'tagStatus': 'TAGGED'
            }
        )
            .build_full_result()
    )
    list_of_images = results.get('imageIds')
    return list_of_images

def filter_images_by_regex(list_of_images):
    """ 
        Description: the function gets list of images ID and returns their tag names as list
        INPUT: list of image ids (string)
        OUTPUT: list of images tags (string)
    """
    list_of_images_to_delete = []
    for image in list_of_images:
        tag = image['imageTag']
        if re.search(regex, tag):
            list_of_images_to_delete.append(tag)
    print(list_of_images_to_delete)        
    return list_of_images_to_delete

def delete_images(list_of_images_to_delete):
    """ 
        Description: Deletes images by image tag
        INPUT: list of image tags (string)
    """
    global regex
    json_list_of_images_to_delete = create_json_to_delete_image_api(list_of_images_to_delete)
    print("deleting {}".format(list_of_images_to_delete))
    if dry_run:
        print("this is dry run")
        return
    if json_list_of_images_to_delete and not dry_run:
        response = client.batch_delete_image(
            **config,
            imageIds=json_list_of_images_to_delete
        )
        print(response)

    else:
        print("no images that strats with {}".format(regex.strip("^")))
     

def create_json_to_delete_image_api(list_of_images_to_delete):
    """ 
        Description: Convert list of tags(string) to a list of json objects {imageTag:$value}
        INPUT: list of image tags (string)
    """    
    json_list_of_images_to_delete = []
    for image in list_of_images_to_delete:
        json_list_of_images_to_delete.append({"imageTag":image})
    return json_list_of_images_to_delete


def handle_argumets():
    """ 
        Description: Gets arguments from argparse and updates the global variables (config and regex)
    """    
    global regex
    global config
    global dry_run
    parser = argparse.ArgumentParser("delete images")
    parser.add_argument("--regex", help="regex pattern for images to delete", required=True)
    parser.add_argument("--registry_id", help="the registry id you'd like to work on", required=True)
    parser.add_argument("--repository_name", help="the repository name you'd like to work on", required=True)
    parser.add_argument("--dry", help="dry run",type=bool)

    args = parser.parse_args()
    regex = args.regex
    dry_run = args.dry
    config = {'registryId': args.registry_id, 'repositoryName': args.repository_name}

def main():
    handle_argumets()
    list_of_images = get_all_images_from_ecr()
    list_of_images_to_delete = filter_images_by_regex(list_of_images)
    delete_images(list_of_images_to_delete)


if __name__ == '__main__':
    main()
