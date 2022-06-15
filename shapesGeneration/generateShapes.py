from PIL import Image, ImageDraw
import random
import math

from pyparsing import nums

img_size = 512
shapes_size = img_size / 2

for i in range(10001, 20001):
    file_label = f"{i:06d}"
    image = Image.new('RGB', (img_size, img_size), 'white') 
    draw = ImageDraw.Draw(image)

    

    numShapes = random.randint(3,5)
    f = open("data/labels/"+file_label+".txt", "w")

    for i in range(1, numShapes):
        color = ['red', 'blue', 'green', 'cyan', 'orange', 'purple']
        colorNum = random.randint(0, 5)
        shapeColor = color[colorNum]
        coordinate = i % 4
        if (coordinate == 0):
            x_offset = 0
            y_offset = 0
        elif coordinate == 1:
            x_offset = img_size / 2
            y_offset = 0
        elif coordinate == 2:
            x_offset = 0
            y_offset = img_size / 2
        else:
            x_offset = img_size / 2
            y_offset = img_size / 2

        shape = random.randint(1,3)
        # 1 is rectangle
        if (shape == 1):
            x1 = random.randint(1,img_size / 2) + x_offset
            y1 = random.randint(1,img_size / 2) + y_offset
            x2 = random.randint(img_size / 4 ,img_size) + x_offset
            y2 = random.randint(img_size / 4 ,img_size) + y_offset

            x = abs(x1+x2) / 2
            y = abs(y1+y2) / 2
            w = abs(x1-x2)
            h = abs(y1-y2)

            while float(x/img_size) + float(w/img_size) / 2 > 1 or float(y/img_size) + float(h/img_size) > 1 or w < img_size / 16 or h < img_size / 16:
                x1 = random.randint(1,img_size) + x_offset
                y1 = random.randint(1,img_size) + y_offset
                x2 = random.randint(img_size / 4 ,img_size) + x_offset
                y2 = random.randint(img_size / 4 ,img_size) + y_offset

                x = abs(x1+x2) / 2
                y = abs(y1+y2) / 2
                w = abs(x1-x2)
                h = abs(y1-y2)

            draw.rectangle((x1, y1, x2, y2), fill=shapeColor, outline=shapeColor) 
            
            f.write("1 " + str("{:.9f}".format(float(x/img_size))) + " " 
            + str("{:.9f}".format(float(y/img_size))) + " " 
            +str("{:.9f}".format(float(w/img_size))) + " "
            +str("{:.9f}".format(float(h/img_size))) + "\n")
            
        # 2 is circle
        elif shape == 2:
            x1 = random.randint(1,img_size) + x_offset
            y1 = random.randint(1,img_size) + y_offset
            width = random.randint(img_size / 8, img_size / 2)

            while float((x1+(width/2))/img_size) + float(width/img_size) / 2 > 1 or float((y1+(width/2))/img_size) + float(width/img_size) / 2 > 1 or width > shapes_size:
                x1 = random.randint(1,img_size) + x_offset
                y1 = random.randint(1,img_size) + y_offset
                width = random.randint(img_size / 8, img_size / 2)

            draw.ellipse((x1, y1, x1 + width, y1 + width), fill = shapeColor, outline =shapeColor)

            f.write("2 " + str("{:.9f}".format(float((x1+(width/2))/img_size))) + " " 
            + str("{:.9f}".format(float((y1+(width/2))/img_size))) + " " 
            +str("{:.9f}".format(float(width/img_size))) + " "
            +str("{:.9f}".format(float(width/img_size))) + "\n")
        # 3 is triangle
        else:
            x1 = random.randint(1,img_size / 2) + x_offset
            y1 = random.randint(1,img_size / 2) + y_offset
            x2 = random.randint(img_size / 4 ,img_size) + x_offset
            y2 = random.randint(img_size / 4 ,img_size) + y_offset
            x3 = int((x1 + x2 + math.sqrt(3)*(y1 - y2))/2)
            y3 = int((y1 + y2 + math.sqrt(3)*(x2 - x1))/2)

            # of GT bounding box
            top = min(y1, y2, y3)
            bottom = max(y1, y2, y3)
            right = max(x1, x2, x3)
            left = min(x1, x2, x3)
            width = (right - left)
            height = (bottom - top)
            centerX = left + width / 2
            centerY = top + height / 2

            while float(centerX/img_size) + float(width/img_size) / 2 > 1 or float(centerY/img_size) + float(height/img_size) / 2 > 1 or math.dist([x1, y1], [x2, y2]) > shapes_size:
                x1 = random.randint(1,img_size / 2) + x_offset
                y1 = random.randint(1,img_size / 2) + y_offset
                x2 = random.randint(img_size / 4 ,img_size) + x_offset
                y2 = random.randint(img_size / 4 ,img_size) + y_offset
                x3 = int((x1 + x2 + math.sqrt(3)*(y1 - y2))/2)
                y3 = int((y1 + y2 + math.sqrt(3)*(x2 - x1))/2)

                top = min(y1, y2, y3)
                bottom = max(y1, y2, y3)
                right = max(x1, x2, x3)
                left = min(x1, x2, x3)
                width = (right - left)
                height = (bottom - top)
                centerX = left + width / 2
                centerY = top + height / 2

            draw.polygon([(x1,y1), (x2, y2), (x3, y3)], fill = shapeColor)

            f.write("3 " + str("{:.9f}".format(float(centerX/img_size))) + " " 
            + str("{:.9f}".format(float(centerY/img_size))) + " " 
            +str("{:.9f}".format(float(width/img_size))) + " "
            +str("{:.9f}".format(float(height/img_size))) + "\n")

    image.save('data/images/'+file_label+'.jpg')
    f.close()


    