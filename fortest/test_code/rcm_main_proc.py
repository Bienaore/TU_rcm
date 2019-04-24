# coding=utf-8
from multiprocessing.dummy import Pool as ThreadPool
from rcm import *

he_dir = os.getcwd() + "/HE_data"
masson_dir = os.getcwd() + "/MASSON_data"


def persist(patient_id, slide_type, set_start_row=False):
	file_path = []
	if slide_type is "MASSON":
		indexes = os.listdir(masson_dir)
		# indexes.sort(key=lambda file_name: int(file_name[:5]))
		# indexes.sort(key=lambda file_name: int(file_name[11:12]))
		indexes.sort()
		for index in indexes:
			if int(index.split("_")[0]) == int(patient_id.split("/")[1]):  # no fibrosis_block.txt
				file_path.append(index)
	else:
		indexes = os.listdir(he_dir)
		# indexes.sort(key=lambda file_name: int(file_name[:5]))
		# indexes.sort(key=lambda file_name: int(file_name[11:12]))
		indexes.sort()
		for index in indexes:
			if int(index.split("_")[0]) == int(patient_id.split("/")[1]):
				file_path.append(index)
	for f in file_path:
		xls_persist_slide(f, slide_type, set_start_row)
	pass


# write test image

def run(start_patient, end_patient, replenish=None, he=True, masson=False, server=False, file_type='.ndpi'):
	if replenish is not None:
		slide_proc(patient_id=start_patient - 1, start=replenish[0], end=replenish[1], he=he, masson=masson,
		           set_hand_drawn=True, server=server, file_type=file_type)
	for i in xrange(start_patient, end_patient):
		slide_proc(patient_id=i, start=0, end=6, he=he, masson=masson, set_hand_drawn=True, server=server,
		           file_type=file_type)
	pass


def run_parallel(start_patient, end_patient, replenish=None, he=True, masson=False, server=False,
                 file_type='.ndpi', slide_type='RCM', threads=12):
	pool = ThreadPool(threads)
	task_list = []
	
	if replenish is not None:
		task_list.append(
			[start_patient - 1, replenish[0], replenish[1], he, masson, True, server, file_type, slide_type])
	# slide_proc(patient_id=start_patient - 1, start=replenish[0], end=replenish[1], he=he, masson=masson,
	#            set_hand_drawn=True, server=server, file_type=file_type)
	for i in xrange(start_patient, end_patient):
		task_list.append([i, 0, 6, he, masson, True, server, file_type, slide_type])
	# slide_proc(patient_id=i, start=0, end=6, he=he, masson=masson, set_hand_drawn=True, server=server,
	#            file_type=file_type)
	pool.map(slide_proc, task_list)
	pool.close()
	pool.join()
	pass


if __name__ == '__main__':
	init_test_proc()
	# masson_test_proc()
	# ============= write test images ================= #
	# MASSON: 41
	# HE : 20
	# for i in xrange(41, 42):  # MASSON RCM
	# for i in xrange(18, 20):  # HE RCM
	# for i in xrange(0, 4):  # MASSON HCM
	# 	# MASSON:
	# 	slide_path = get_patient_image_path(i, return_type="MASSON", file_type='.mrxs',
	# 	                                    for_split=True, is_masson=True, is_he=False, is_hcm=True)
	# 	write_test_img(slide_path[0], is_masson=True, saved_img_level=6)
	
	# HE
	# slide_path = get_patient_image_path(i, return_type="HE", file_type='.mrxs',
	#                                     for_split=True, is_masson=False, is_he=True)
	# write_test_img(slide_path[0], is_masson=False, saved_img_level=6)
	
	# ===================================================#
	
	# persist process begin#################
	# for i in xrange(3, 4):
	# 	slide_proc(patient_id=i, start=3, end=6, he=True, masson=False, set_hand_drawn=True)
	
	# ================ RUN ================= #
	# run(1, 26, replenish=(0, 6), server=True, he=False, masson=True, file_type='.mrxs')
	run_parallel(1, 26, replenish=(0, 6), server=True, he=False, masson=True, file_type='.mrxs')
	# ================ RUN ==================#
	
	# ================ PERSIST ===============#
	# for i in range(0, 26):
	# persist(masson_patients[i], slide_type="MASSON")
	# persist(masson_patients[i], slide_type="HE")
	# for i in range(0, 20):
	# 	persist(he_patients[i], slide_type="HE")
	# ================ PERSIST ===============#
	
	'''
	deal with hand_drawn pics
	'''
	# image_path = '/home/zhourongchen/lys/rcm_project/fortest/test_code/HE_image/25845/whole/25845_slide0.jpg'
	# image_path = '/home/zhourongchen/lys/rcm_project/fortest/test_images/HE/29708/test_35730-2_LI.jpg'
	# image_path = '/home/zhourongchen/lys/rcm_project/fortest/test_images/HE/29708/test_29708-1_LI2.jpg'
	# for test only
	# he_test_proc()
	# for i in xrange(2, 3):
	# slide_proc(patient_id=i, start=0, end=1, he=True, masson=False, set_hand_drawn=True, hand_drawn_img=image_path)
	# he_slide_path, masson_slide_path = get_image_path(i)
	# write_test_img(he_slide_path, saved_img_level=6)
	
	# persist(he_patients[1], slide_type="HE")
	
	# masson_test_proc()
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()
	
	# he test_images
	# he_test_proc()
	# he_whole_res.append(he_test_proc())
	# he_statics_persistence(he_whole_res)
	# 空泡 心肌细胞核 非心肌细胞核 区域总面积 列表[编号，细胞核面积，细胞核周长]
	# cv2.waitKey(0)
	cv2.destroyAllWindows()
	
	# print dimension
	'''
	(1, 136, 236, 919452, [[3, 355, 99.94112491607666], [8, 322, 67.4558436870575], [9, 541, 161.01219260692596], [10, 329, 73.4558436870575], [12, 911, 152.36753106117249], [14, 606, 104.66904675960541], [18, 436, 87.94112491607666], [20, 732, 107.35533845424652], [24, 435, 89.35533845424652],
	'''
# img = numpy.array(slide.read_region((0, 0), level, workingDimensions))
# grey = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
# greyret, greyimg = cv2.threshold(grey, 225, 255, cv2.THRESH_BINARY_INV)
# dst = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
# average_greyimg = cv2.blur(greyimg, (n, n))
# cv2.imshow('adaptive threshold', dst)
# cv2.imshow('greyimg', greyimg)
# cv2.imshow('average_grey', average_greyimg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# print dimension

# img = np.array(slide.read_region((0, 0), level, workingDimensions))
#
# b, g, r, a = cv2.split(img)
# rgbimg = cv2.merge((r, g, b))
# cv2.imwrite("test_images/he_rgbimg.jpg", rgbimg)
# hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
# cv2.imwrite("test_images/he_hsv.jpg", hsv)
# greyimg = cv2.inRange(hsv, (0, 20, 0), (180, 255, 255))
# cv2.imwrite("test_images/he_grey.jpg", greyimg)

# fibrosis = cv2.inRange(hsv, (90, 20, 0), (150, 255, 255))
# cv2.imshow("fibrosis",fibrosis)
# averagegreyimg = cv2.blur(greyimg, (30, 30))
# cv2.imshow('he_average grey img', averagegreyimg)
# cv2.imwrite("test_images/he_average_grey_img.jpg", averagegreyimg)

# ret, erode = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
# erode = cv2.adaptiveThreshold(averagegreyimg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
# erode = cv2.erode(erode, kernel, iterations=13)
# cv2.imshow("after erosion", erode)
# cv2.imwrite("test_images/he_after_erosion.jpg", erode)

# cv2.imshow("")
# get rid of XIAOLIANG

# ret, averimage = cv2.threshold(averagegreyimg, 120, 255, cv2.THRESH_BINARY)
# averimage, avercnts, averhierarchy = cv2.findContours(averimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cv2.imshow("aver image", averimage)
# overall contour

# image, cnts, hierarchy = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cv2.imshow("contour after erosion", erode)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
