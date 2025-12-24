from ultralytics import YOLO

# Load a model
model = YOLO(r"H:\pycharm_project\PI-MAPP\project\huawei_platelet_seg\pt\best.pt")  # load an official model

# Predict with the model
results = model.predict(source=r"H:\pycharm_project\PI-MAPP\project\huawei_platelet_seg\dataset_demo\images\train",save=True,save_txt=True)  # predict on an image

# Access the results
# for result in results:
#     # xy = result.masks.xy  # mask in polygon format
#     xyn = result.masks.xyn  # normalized
#     masks = result.masks.data  # mask in matrix format (num_objects x H x W)