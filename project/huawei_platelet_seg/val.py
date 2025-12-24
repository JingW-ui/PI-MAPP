from ultralytics import YOLO



if __name__ == '__main__':
    # Load a pre-trained YOLO11 model
    model = YOLO(r"H:\pycharm_project\PI-MAPP\project\huawei_platelet_seg\runs\segment\train\weights\best.pt")


    metrics = model.val(data="cfg.yaml")

    print(f"Validation mAP50-95: {metrics.box.map}")
