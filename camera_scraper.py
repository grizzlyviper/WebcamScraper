from datetime import datetime
import time, requests, os
import glob
import boto3
import pandas as pd
# os.chdir('C:\\Users\\alps\\Documents\\camera_scraper_beta1')
s3 = boto3.client('s3')
S3_BUCKET_NAME = 'filescrape'
path = '/Users/allan/Downloads/traffic-cam-scraper/camera/MontezumaRoad/'
#path='C:\\Users\\alps\\Documents\\camera_scraper_beta1\\traffic-cam-scraper\\camera\\redmtn\\'
# from botocore.exceptions import NoCredentialsError


url_front = "https://cocam.carsprogram.org/Live_View/US6216East.jpg?1674438600000" #portion of url before camera id
url_end = "" # portion url after the camera ID
camera_ids = ['MontezumaRoad'] # Camera id (part of url that changes to indicate camera)
img_type = "jpg" # File extention used when saving image files

img_dir = "./camera" # Directory where subdirectories for each camera will be stored
capture_interval = 10 # Interval between end of last capture and start of current capture

df = pd.read_csv('MtnCameras.csv')
for i ,row in df.iterrows():
        value = print(f"{row['url']}")

def capture_all_cameras():
    currentTimeDate = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    print(f"Capture at {currentTimeDate}")
    for camera in camera_ids:
        # Combines the URL
        url = f'{url_front}{camera}{url_end}'
        try:
            r = requests.get(url, allow_redirects=True)
            open(f'{img_dir}/{camera}/camera{camera}-{currentTimeDate}.{img_type}', 'wb').write(r.content)
            status = "success"
        except requests.ConnectionError:
            status = "ERROR (network)"
        except OSError:
            status = "ERROR (file)"
        except:
            status = "ERROR (other)"
        print(f"\t{camera}  \t\t {status}")


def configure_folders():
     for camera in camera_ids:
        path = f'{img_dir}/{camera}'
        pathExists = os.path.exists(path)
        if not pathExists:
            print(f"Creating path for camera {camera}")
            os.makedirs(path)
        else:
             print(f"Path for camera {camera} exists")

def files():
    list_of_files = glob.glob(path + '*.jpg')
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)

    s3 = boto3.client('s3')
    with open(latest_file, 'rb') as f:
        s3.upload_fileobj(f, S3_BUCKET_NAME, latest_file)


camera_ids.sort()
configure_folders()
while(True):
    capture_all_cameras()
    time.sleep(capture_interval)
    files()




