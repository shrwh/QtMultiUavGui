import torch
from models.experimental import attempt_load
from utils.datasets import LoadImages
from utils.general import check_img_size, non_max_suppression, scale_coords, set_logging
from utils.torch_utils import select_device, time_synchronized
import multiprocessing as mp

# 目标检测
def detect_center(frame_cap,condition:mp.Condition,conn:mp.Pipe):
    weights, imgsz = '/home/nvidia/yolov3/best.pt', 640
    # Initialize
    set_logging()
    device = select_device('')
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size
    names = model.module.names if hasattr(model, 'module') else model.names  # get class names
    if half:
        model.half()  # to FP16

    while True:
        info={"red":None,"yellow":None}
        with condition:
            condition.wait()
        image = frame_cap.frame
        # image = cv2.imread('000125.jpg')
        print("begin detect")
        if image is None:
            continue
        img, im0s = LoadImages(image, img_size=imgsz, stride=stride).get_img()

        # Run inference
        if device.type != 'cpu':
            model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
        #t0 = time.time()

        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment=True)[0]

        # Apply NMS
        pred = non_max_suppression(pred, agnostic=True, max_det=300)
        t2 = time_synchronized()
        # Process detections
        for i, det in enumerate(pred):  # detections per image

            '''if webcam:  # batch_size >= 1
                p, s, im0, frame = path[i], f'{i}: ', im0s[i].copy(), dataset.count
            else:'''
            s, im0 = '', im0s.copy()
            s += '%gx%g ' % img.shape[2:]  # print string
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                det_new = reversed(det)
                # Write results
                for *xyxy, conf, cls in det_new:
                    ans = torch.tensor(xyxy).view(1, 4).tolist()[0]
                    ans = [(ans[1] + ans[3]) / 2, (ans[0] + ans[2]) / 2]
                    if (not int(cls)):
                        info['red'] = ans
                    else:
                        info['yellow'] = ans
                print(info['red'])
            else:
                info['red'] = None
                info['yellow'] = None

        print(info)
        conn.send(info)
            # Print time (inference + NMS)
            # print(f'{s}Done. ({t2 - t1:.3f}s)')
            # print("end detect one image")