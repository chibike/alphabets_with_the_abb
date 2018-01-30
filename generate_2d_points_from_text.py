import cv2
import time
import turtle
import numpy as np
import matplotlib.pyplot as plt

def get_2d_points(text = "c"):
    img_size = (500,500,3)
    start_position = (50,50)
    font_size = 2
    pixel_width = 5

    img = np.zeros(img_size, np.uint8)

    timg = cv2.putText(img,text, start_position, cv2.FONT_HERSHEY_SIMPLEX, font_size, (255,255,255), pixel_width, cv2.LINE_8)
    imgray = cv2.cvtColor(timg, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(img, contours, -1, (0,255,0), 3)

    points_array = []
    for contour in contours:
        points = contour.ravel()
        points.shape = (len(contour),2)

        points = np.append(points, [points[0]], axis=0)
        points_array.append(points)

    # Convert image axis to cartesian axis (flip y-axis)
    for points in points_array:
        foo = np.array(points[:,1], np.float16)
        foo -= float(img_size[1])
        foo *= -1.0
        points[:,1] = np.array(foo, np.uint8)

    mnx = img_size[0]; mny = img_size[1]
    for points in points_array:
        mnx = min(mnx, min(points[:,0]))
        mny = min(mny, min(points[:,1]))

    #Normalize
    for points in points_array:
        points[:,0] -= mnx
        points[:,1] -= mny

    return points_array

def get_2d_points_from_image(image_name="E:\Batman.png", normalize=False):
    img = cv2.imread(image_name)
    img_size = img.shape
    
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(img, contours, -1, (0,255,0), 3)

    #plt.imshow(img)
    #plt.show()

    points_array = []
    for contour in contours:
        points = contour.ravel()
        points.shape = (len(contour),2)

        points = np.append(points, [points[0]], axis=0)
        xs,ys = list(zip(*points.tolist()))
        foo = list(zip(ys, xs))
        foo.append(foo[1])
        points = np.array(foo)
        points_array.append(points)

    points_array = points_array[1:]
    mnx = img_size[0]; mny = img_size[1]
    mxx = img_size[0]; mxy = img_size[1]
    for points in points_array:
        mnx = min(mnx, min(points[:,0]))
        mny = min(mny, min(points[:,1]))
        mxx = max(mnx, max(points[:,0]))
        mxy = max(mny, max(points[:,1]))
    #print (mnx, mny),(mxx, mxy)

    if normalize:
        #Normalize
        for points in points_array:
            points[:,0] -= mnx
            points[:,1] -= mny
        mnx = img_size[0]; mny = img_size[1]
        mxx = img_size[0]; mxy = img_size[1]
        for points in points_array:
            mnx = min(mnx, min(points[:,0]))
            mny = min(mny, min(points[:,1]))
            mxx = max(mnx, max(points[:,0]))
            mxy = max(mny, max(points[:,1]))
        print (mnx, mny),(mxx, mxy)

    return points_array

def draw_points(points, offset=(0,0), scale=3, flip_offset=283, approach_offset=30):
    turtle.penup()
    
    for x,y in points:
        point = [x,y,0]
        print "MoveJ Offs([{0},[0,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]], 0, 0, 0),v80,fine,tool0\WObj:=WorkSurface;".format(str(point))
        turtle.goto((x + offset[0])*scale,(y + offset[1])*scale)
        turtle.pendown()
        time.sleep(0.1)
    turtle.penup()

def print_rapid_data(points, index=0, offset=(0,0), scale=(1.0,1.0)):
    string = ""

    xs = []
    ys = []
    for x,y in points:
        x = (float(x) + offset[0]) * scale[0]
        y = (float(y) + offset[1]) * scale[1]
        string += str([x,y,0]) + ","

        xs.append(x)
        ys.append(y)

    min_x = min(xs); max_x = max(xs)
    min_y = min(ys); max_y = max(ys)
    
    print "VAR pos pos{0}{1} := [{2}];\n".format(index,"{"+str(len(points))+"}", string[:-1])

    return [(min_x, min_y), (max_x, max_y)]

def print_as_rapid_function(points_array, function_name="DrawArtWork_1", work_surface="WorkSurface", tool_object="Alex_Pen_ABB", offset=(0,0), scale=(1.0,1.0)):
    indentation = "    "

    print indentation + "PROC {0}(num font_size, speeddata approach_speed, speeddata write_speed, num x_offset, num y_offset, num z_offset, num penup_offset)".format(function_name)
    print indentation + indentation + "! Define all points for artwork"

    counter = 0
    for points in points_array:
        string = ""
        for x,y in points:
            x = (float(x) + offset[0]) * scale[0]
            y = (float(y) + offset[1]) * scale[1]
            string += str([x,y,0]) + ","
        print indentation + indentation + "VAR pos pos{0}{1} := [{2}];".format(counter,"{"+str(len(points))+"}", string[:-1])
        counter += 1
    print indentation + indentation

    print indentation + indentation + "! Define variables to be used while drawing"
    print indentation + indentation + "VAR pos position := [0,0,0];"
    print indentation + indentation + "VAR robtarget next_target := [[0,0,0],[0,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];"
    print indentation

    print indentation + indentation + "! Update the penup_offset based on the z_offset"
    print indentation + indentation + "penup_offset := z_offset + penup_offset;"
    print indentation + indentation

    for index in xrange(len(points_array)):
        position_name = "pos" + str(index)

        print indentation + indentation + "! Raise pen to avoid drawing of surface while moving to the new approach position"
        print indentation + indentation + "position := " + position_name + "{1} * font_size;"
        print indentation + indentation + "next_target.trans := position;"
        print indentation + indentation + "MoveJ Offs(next_target, x_offset, y_offset, penup_offset),approach_speed,fine,{0}\\WObj:={1};".format(tool_object, work_surface)
        print indentation + indentation
        print indentation + indentation + "! Drop pen"
        print indentation + indentation + "MoveL Offs(next_target, x_offset, y_offset, z_offset),approach_speed,fine,{0}\WObj:={1};".format(tool_object, work_surface)
        print indentation + indentation
        print indentation + indentation + "FOR index FROM 1 TO Dim({0}, 1) DO".format(position_name)
        print indentation + indentation + indentation + "position := " + position_name + "{index} * font_size;"
        print indentation + indentation + indentation + "next_target.trans := position;"
        print indentation + indentation + indentation
        print indentation + indentation + indentation + "MoveL Offs(next_target, x_offset, y_offset, z_offset),approach_speed,fine,{0}\WObj:={1};".format(tool_object, work_surface)
        print indentation + indentation + "ENDFOR"
        print indentation + indentation
        print indentation + indentation + "! Raise pen"
        print indentation + indentation + "MoveL Offs(next_target, x_offset, y_offset, penup_offset),approach_speed,fine,{0}\WObj:={1};".format(tool_object, work_surface)
        print indentation + indentation

    print indentation + "ENDPROC"
    
    

def test_1(text="Blink"):
    points_array = get_2d_points(text)

    for points in points_array:
        print_rapid_data(points)

    for points in points_array:
        draw_points(points)

def test_2():
    characters = [' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~']
    for character in characters:
        print "Data for character: {0}".format(character)
        points_array = get_2d_points(text=character)
        for points in points_array:
            print_rapid_data(points)
        print "\n\n"

def generate_rapid_code_from_text_image(text_image_file="text_image.txt"):
    cmd_1 = "DrawString "+ '"{0}"' + ", font_size, v500, v800, x_offset, y_offset, 0, 30;"
    cmd_2 = "y_offset := y_offset + line_height;"

    f = open(text_image_file, 'r')
    while True:
        text = f.readline().strip('\n').replace('"', '""').replace("\\", "\\\\")
        if not text:
            break
        print cmd_1.format(text)
        print cmd_2
    print text
    f.close()

def test_3():
    characters = [' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~']

    mxmxx = 0; mxmxy = 0
    for character in characters:
        points_array = get_2d_points(text=character)
        mxx = 0; mxy = 0
        for points in points_array:
            mxx = max(mxx, max(points[:,0]))
            mxy = max(mxy, max(points[:,1]))
        print "Character: '{0}' has ({1},{2}) dimens".format(character, mxx, mxy)

        mxmxx = max(mxx, mxmxx)
        mxmxy = max(mxy, mxmxy)
    print "The ultimate dimens is ({0},{1}) dimens".format(mxmxx, mxmxy)

def test_4(image_name="artwork_01.jpg"):
    points_array = get_2d_points_from_image(image_name)[1:]
    response = []

    index = 0
    for points in points_array:
        response.append( print_rapid_data(points, index, offset=(-62,-17), scale=(0.7,0.7)) )
        index += 1

    for points in points_array:
        draw_points(points, scale=1, offset=(-200,-200))

    mins, maxs = list(zip(*response))

    min_xs, min_ys = list(zip(*mins))
    max_xs, max_ys = list(zip(*maxs))

    min_x = min(min_xs)
    max_x = max(max_xs)

    min_y = min(min_ys)
    max_y = max(max_ys)

    print "X Range: {0} - {1}".format(min_x, max_x)
    print "Y Range: {0} - {1}".format(min_y, max_y)

def test_5(image_name="images/img_002.jpg"):
    points_array = get_2d_points_from_image(image_name)
    print_as_rapid_function(points_array, function_name="DrawArtWork_1", work_surface="WorkSurface", tool_object="Alex_Pen_ABB", offset=(0,0), scale=(1.0,1.0))

#generate_rapid_code_from_text_image()

#test_1()
test_2()
#test_3()
#test_4("images/art_border.jpg")
#test_5("raj_wolf.jpg")
#test_5()#test_5("images/art_border.jpg")

#plt.imshow(img)
#plt.show()
