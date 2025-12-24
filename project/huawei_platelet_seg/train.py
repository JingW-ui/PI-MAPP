from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO("pt/best.pt")  # load a pretrained model (recommended for training)

    # Train the model
    results = model.train(data="cfg.yaml", epochs=100, imgsz=512)