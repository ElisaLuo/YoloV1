import torch
import torchvision.transforms as transforms
import torch.optim as optim
import torchvision.transforms.functional as FT
from tqdm import tqdm
from torch.utils.data import DataLoader
from model import Yolov1
from dataset import VOCDataset
from utils import (
    non_max_suppression,
    mean_average_precision,
    intersection_over_union,
    cellboxes_to_boxes,
    get_bboxes,
    plot_heatmap,
    plot_image,
    convert_cellboxes,
    save_checkpoint,
    load_checkpoint,
)
from loss import YoloLoss

seed = 123
torch.manual_seed(seed)

# Hyperparameters etc. 
LEARNING_RATE = 2e-5
#DEVICE =  "cuda" if torch.cuda.is_available else "cpu"
DEVICE = "cpu"
BATCH_SIZE = 16
WEIGHT_DECAY = 0
EPOCHS = 1000
NUM_WORKERS = 2
PIN_MEMORY = True
LOAD_MODEL = True
LOAD_MODEL_FILE = "overfit.pth.tar"
IMG_DIR = "shapesGeneration/data/images"
LABEL_DIR = "shapesGeneration/data/labels"


class Compose(object):
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, img, bboxes):
        for t in self.transforms:
            img, bboxes = t(img), bboxes

        return img, bboxes


transform = Compose([transforms.Resize((448, 448)), transforms.ToTensor(),])

def test_fn(test_loader, optimizer, model):
    with torch.no_grad(): 
        for x, y, z in test_loader:
            x = x.to(DEVICE)
            for idx in range(len(x)):
                bboxes = cellboxes_to_boxes(model(x))
                bboxes = non_max_suppression(bboxes[idx], iou_threshold=0.5, threshold=0.4, box_format="midpoint")
                plot_image(x[idx].permute(1,2,0).to("cpu"), bboxes, z[idx])
            import sys
            sys.exit()

def test_fn_v2(test_loader, optimizer, loss_fn, model, f):
    loop = tqdm(test_loader, leave=True)
    mean_loss = []
    
    for batch_idx, (x, y, z) in enumerate(loop):
        x, y = x.to(DEVICE), y.to(DEVICE)
        out = model(x)
        converted_pred = convert_cellboxes(out).reshape(out.shape[0], 7 * 7, -1)
        #for idx in range(len(x)):
            #bboxes = cellboxes_to_boxes(out)
            #plot_heatmap(converted_pred[idx], z[idx])
            #bboxes = non_max_suppression(bboxes[idx], iou_threshold=0.5, threshold=0.7, box_format="midpoint")
            #plot_image(x[idx].permute(1,2,0).to("cpu"), bboxes, z[idx])
        #plot_heatmap(out)
        loss = loss_fn(out, y)
        mean_loss.append(loss.item())
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # update progress bar
        loop.set_postfix(loss=loss.item())
    f.write(str(sum(mean_loss)/len(mean_loss)) + "\n")
    print(f"Mean loss was {sum(mean_loss)/len(mean_loss)}")

def main():
    model = Yolov1(split_size=7, num_boxes=2, num_classes=20).to(DEVICE)
    optimizer = optim.Adam(
        model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY
    )

    if LOAD_MODEL:
        load_checkpoint(torch.load(LOAD_MODEL_FILE, map_location=torch.device('cpu')), model, optimizer)

    test_dataset = VOCDataset(
        "shapesGeneration/data/testSmall.csv", 
        transform=transform, 
        img_dir=IMG_DIR, 
        label_dir=LABEL_DIR,
    )

    test_loader = DataLoader(
        dataset=test_dataset,
        batch_size=BATCH_SIZE,
        num_workers=NUM_WORKERS,
        pin_memory=PIN_MEMORY,
        shuffle=False,
        drop_last=False,
    )
    f = open("trainingData.txt", "a")
    loss_fn = YoloLoss()
    for epoch in range(EPOCHS):
        pred_boxes, target_boxes = get_bboxes(
            test_loader, model, iou_threshold=0.5, threshold=0.7
        )

        mean_avg_prec = mean_average_precision(
            pred_boxes, target_boxes, iou_threshold=0.5, box_format="midpoint"
        )

        print(f"Test mAP: {mean_avg_prec}")
        f.write(str(epoch) + " " + str(mean_avg_prec) + " ")

        test_fn_v2(test_loader, optimizer, loss_fn, model, f)

if __name__ == "__main__":
    main()