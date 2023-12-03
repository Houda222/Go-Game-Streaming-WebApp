from utils_ import *
import math, copy



class GoBoard:

    def __init__(self, model):

        self.model = model
        self.frame = None
        self.results = None
        self.tranformed_image = None
        self.annotated_frame = None
        self.state = None
        
        
    def get_state(self):
        return copy.deepcopy(self.state)

    
    def process_frame(self, frame):
        self.frame = frame
        self.results = self.model(frame)
        self.annotated_frame = self.results[0].plot(labels=False, conf=False)
        # imshow_(self.annotated_frame)
        
        input_points = get_corners(self.results)

        output_edge = 600
        output_points = np.array([[0, 0], [output_edge, 0], [output_edge, output_edge], [0, output_edge]], dtype=np.float32)

        perspective_matrix = cv2.getPerspectiveTransform(input_points, output_points)
        self.transformed_image = cv2.warpPerspective(frame, perspective_matrix, (output_edge, output_edge))
        
        vertical_lines, horizontal_lines = lines_detection(self.results, perspective_matrix)
        
        vertical_lines = removeDuplicates(vertical_lines)
        horizontal_lines = removeDuplicates(horizontal_lines)
        
        vertical_lines = restore_and_remove_lines(vertical_lines)
        horizontal_lines = restore_and_remove_lines(horizontal_lines)

        vertical_lines = add_lines_in_the_edges(vertical_lines, "vertical")
        horizontal_lines = add_lines_in_the_edges(horizontal_lines, "horizontal")
        
        vertical_lines = removeDuplicates(vertical_lines)
        horizontal_lines = removeDuplicates(horizontal_lines)
        
        black_stones = get_key_points(self.results, 0, perspective_matrix)
        white_stones = get_key_points(self.results, 6, perspective_matrix)

        cluster_1 = vertical_lines[(vertical_lines<=600).all(axis=1) & (vertical_lines>=0).all(axis=1)]
        cluster_2 = horizontal_lines[(horizontal_lines<=600).all(axis=1) & (horizontal_lines>=0).all(axis=1)]
        
        if len(cluster_1) != 19 or len(cluster_2) != 19:
            raise Exception(f"Incorrect number of lines was detected: {len(cluster_1)} vertical lines and {len(cluster_2)} horizontal lines")
        
        # # img = np.copy(self.transformed_image)
        # draw_lines(cluster_1, self.transformed_image)
        # # img = np.copy(self.transformed_image)
        # draw_lines(cluster_2, self.transformed_image)
        # # imshow_(img)
        
        intersections = detect_intersections(cluster_1, cluster_2, self.transformed_image)
                
        if len(intersections) == 0:
            raise Exception(">>>>>No intersection were found!")
        if len(intersections) != 361:
            print(">>>>>Not all intersections were found")
        self.assign_stones(white_stones, black_stones, intersections)
        

    def assign_stones(self, white_stones_transf, black_stones_transf, transformed_intersections):
        
        self.map = map_intersections(transformed_intersections)
        self.state = np.zeros((19, 19, 2))
        
        for stone in white_stones_transf:
            
            cv2.circle(self.transformed_image, np.array(stone).astype(dtype=np.int32), 3, (0, 0, 255), 2)
            
            nearest_corner = None
            closest_distance = 100000
            for inter in transformed_intersections:
                distance = math.dist(inter, stone)
                if distance < closest_distance:
                    nearest_corner = tuple(inter)
                    closest_distance = distance
            # cv2.circle(self.transformed_image, np.array(nearest_corner).astype(dtype=np.int32), 3, (0, 255, 0), 2)
            # print("W", stone, self.map[nearest_corner])
            self.state[self.map[nearest_corner][1], self.map[nearest_corner][0], 1] = 1
            cv2.line(self.transformed_image, (int(stone[0]), int(stone[1])), nearest_corner, (0, 255, 255), 2)
            # cv2.putText(self.transformed_image, f"{(self.map[nearest_corner])}", nearest_corner, fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL , fontScale=0.5, color=(0,0,255))
            
                
        for stone in black_stones_transf:
            
            cv2.circle(self.transformed_image, np.array(stone).astype(dtype=np.int32), 3, (0, 0, 255), 2)
            
            nearest_corner = None
            closest_distance = 100000
            for inter in transformed_intersections:
                distance = math.dist(inter, stone)
                if distance < closest_distance:
                    nearest_corner = tuple(inter)
                    closest_distance = distance
            # cv2.circle(self.transformed_image, np.array(nearest_corner).astype(dtype=np.int32), 3, (0, 255, 0), 2)
            # print("B", stone, self.map[nearest_corner])
            self.state[self.map[nearest_corner][1], self.map[nearest_corner][0], 0] = 1
            cv2.line(self.transformed_image, (int(stone[0]), int(stone[1])), nearest_corner, (0, 255, 255), 2)
            # cv2.putText(self.transformed_image, f"{(self.map[nearest_corner])}", nearest_corner, fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL , fontScale=0.5, color=(0,0,255))
        
        # imshow_(self.transformed_image)
