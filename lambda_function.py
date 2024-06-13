import json
import os
import boto3
import trimesh
import warnings

warnings.filterwarnings('ignore')

def lambda_handler(event, context):
    s3 = boto3.client('s3')

    #Different triggers to test the parser, 

    #API Gateway / Function url invocation   
    # file_in = json.loads(event['body'])['file_in']
    # file_out = json.loads(event['body'])['file_out']
    # bucket_name = json.loads(event['body'])['bucket_name']

    #Regular that only works with lambda tester
    # file_in = event['file_in']
    # file_out = event['file_out']
    # bucket_name = event['bucket_name']


    #S3 Upload Trigger
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_in = event['Records'][0]['s3']['object']['key']

    is_stl = file_in.lower().endswith('.stl')
    if is_stl:
        print("The file is already in STL format.")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "The file is already in STL format."})
        }

    file_out = file_in.rsplit('.', 1)[0] + '.stl'

    input_file_path = '../tmp/' + os.path.basename(file_in)
    s3.download_file(bucket_name, file_in, input_file_path)
    
    mesh = trimesh.Trimesh(**trimesh.interfaces.gmsh.load_gmsh(file_name=input_file_path, gmsh_args=[
        ("Mesh.Algorithm", 2),  # Different algorithm types, check them out
        ("Mesh.DrawSkinOnly", 1),  
        ("Mesh.MeshOnlyVisible", 1),  
        ("Mesh.MeshSizeExtendFromBoundary", 0),  
        ("Mesh.CharacteristicLengthFromCurvature", 50),
        ("Mesh.MeshSizeMin", 0.95),
        ("General.NumThreads", 10),  # Multithreading capability
        ("Geometry.OCCFixDegenerated", 1),  
        ("Geometry.OCCFixSmallEdges", 1),  
        ("Geometry.OCCFixSmallFaces", 1),  
        ("Geometry.OCCExportOnlyVisible", 1),  
        ("Geometry.OCCUseGenericClosestPoint", 1),  
        ("Geometry.OldCircle", 1),  
        ("Geometry.OldRuledSurface", 1),  
        ("Mesh.MinimumCirclePoints", 32)
    ]))

    output_file_path = '../tmp/' + os.path.basename(file_out)
    mesh.export(file_type="stl", file_obj=output_file_path)
    
    # Upload output file to S3
    s3.upload_file(output_file_path, bucket_name, file_out)

    result = {
        "meshVolume": mesh.volume,
        "meshArea": mesh.area,
        "dimensionX": mesh.bounds[1][0] - mesh.bounds[0][0],
        "dimensionY": mesh.bounds[1][1] - mesh.bounds[0][1],
        "dimensionZ": mesh.bounds[1][2] - mesh.bounds[0][2],
    }
    
    print(json.dumps(result))

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
