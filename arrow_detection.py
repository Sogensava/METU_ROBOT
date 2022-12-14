import math,cv2,time
import numpy as np

tip_point_global_tuple = []
bottom_point_global_tuple = []
tip_point_global = list(tip_point_global_tuple)


def angle_finder(point1, point2, width_of_image=640, height_of_image=480):
    x1 = point1[0] - width_of_image // 2
    y1 = point1[1] - height_of_image // 2
    x2 = point2[0] - width_of_image // 2
    y2 = point2[1] - height_of_image // 2

    slope = ((x2 - x1) / (y2 - y1))
    result = math.degrees(math.atan(slope))

    if y1 > y2:
        if x1 > x2:
            # print("one")
            return -result

        else:
            # print("two")
            return -result

    else:
        if x1 < x2:
            # print("three")
            return 180 - result

        else:
            # print("four")
            return -(result + 180)

def find_arrow_points(points, convex_hull):
    global tip_point_global_tuple, bottom_point_global_tuple
    length = len(points)
    indices = np.setdiff1d(range(length), convex_hull)

    for i in range(2):
        j = indices[i] + 2
        if j > length - 1:
            j = length - j
        if np.all(points[j] == points[indices[i - 1] - 2]):
            bottom_indice = int((indices[0] + indices[1]) / 2)
            tip_point_global_tuple = tuple(points[j])
            bottom_point_global_tuple = tuple(points[bottom_indice])

def arrow_yaw_ardupilot(colored_image, canny_image, contour_area=2000):
    global vehicle_mode,tip_point_global,arrow_tip,letter_type,again_letter_flag,vx_arrow,vy_arrow,yaw_arrow
    forward_counter = 0

    cv2.putText(colored_image, "Arrow Mode", (0, 180), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255),2)
    contours, hierarchy = cv2.findContours(canny_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if contours != ():
        total_area = 0
        for cnt in contours:
            contour = cv2.contourArea(cnt)
            total_area += contour
        if total_area >= int(len(contours))*contour_area/5:
            for cnt in contours:
                if cv2.contourArea(cnt) > contour_area:
                    peri = cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)
                    hull = cv2.convexHull(approx, returnPoints=False)
                    x, y, w, h = cv2.boundingRect(approx)
                    global check
                    check = False
                    global counter_arrow,arrow_center_stop
                    arrow_center_stop = False
                    cx = int(x + (w / 2))
                    cy = int(y + (h / 2))
                    vx = cx - (frameWidth / 2)
                    vy = (frameHeight / 2) - cy
                    x1_global, y1_global = x + w // 2, y + h // 2
                    sides = len(hull)
                    if sides != 0:
                        if 6 > sides > 3 and sides + 2 == len(approx):
                            points_variable = approx[:, 0, :]
                            hull_variable = hull.squeeze()
                            find_arrow_points(points_variable, hull_variable)
                            arrow_tip = list(tip_point_global_tuple)
                            cv2.drawContours(colored_image, cnt, -1, (0, 255, 0), 3)

                            if arrow_tip != []:
                                vehicle_mode = "Arrow"
                                cv2.circle(colored_image, arrow_tip, 3, (0, 0, 255), cv2.FILLED)
                                # client.hoverAsync()
                                result = angle_finder([x1_global, y1_global], arrow_tip)
                                cv2.putText(colored_image, str(result), arrow_tip, cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0),2)
                                cv2.circle(colored_image, (x + w // 2, y + h // 2), 3, (0, 255, 255), 3)
                                if not arrow_center_stop:
                                    if not check:
                                        if 45 >= vx >= -45 and vy <= 45 and vy >= -45:
                                            counter_arrow += 1
                                            if counter_arrow >= 50:
                                                check = True
                                                arrow_center_stop = True
                                                vx_arrow=1
                                                vy_arrow=0
                                                yaw_arrow=result
                                                again_letter_flag = True
                                                counter_arrow = 0
                                                arrow_tip.clear()
                                                vehicle_mode=None

                                        else:
                                            if vy >= 0 and vx <= 0 or vy <= 0 and vx >= 0:
                                                vx_arrow=-vx
                                                vy_arrow=-vy
                                                yaw_arrow = result
                                                print("Arrow",vx_arrow," ",vy_arrow)


                                            else:
                                                vx_arrow=vx
                                                vy_arrow=vy
                                                yaw_arrow = result
                                                print("Arrow", vx_arrow, " ", vy_arrow)

    #     else:
    #         print("ileri git = düşük alan")
    #         vx_arrow=0.2
    #         vy_arrow=0
    #
    # else:
    #     print("ileri git = kontür yok")
    #     vx_arrow = 0.2
    #     vy_arrow = 0
