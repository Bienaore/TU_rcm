# coding=utf-8
import matplotlib

matplotlib.use('Agg')
import os
import sys
from time import time
from skimage import measure
import matplotlib.pyplot as plt
from scipy.stats import iqr
from module import *

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)

slide_he = []
slide_masson = []
max_level = 0
working_level = 0
max_dimension = ()
working_dimension = ()

he_test_path = []
masson_test_path = []
hand_draw_image_path = []


# img_dir = '/home/zhourongchen/zrc/rcm/images'
# patients = ['/25845', '/28330', '/29708', '/30638', '/31398', '/35485']


def init_test_proc():
	# kk = 1
	# name = '25845-' + str(kk)
	# he_img_name = name + '.ndpi'
	# patient_id = patients[0]
	# global patient_id
	global he_test_path
	global masson_test_path
	he_test_path, masson_test_path = get_patient_image_path(0, return_type="both", is_he=True,
	                                                        is_masson=True)  # test 28330
	global slide_he
	global slide_masson
	#  init
	slide_he = openslide.open_slide(he_test_path[0][0])
	# slide_masson = openslide.open_slide(masson_test_path[0][0])
	global max_dimension
	global max_level
	max_dimension = slide_he.dimensions
	'''
	dimension (81920L, 65536L)
	(1280L, 1024L)
	'''
	# print "dimension", dimension
	max_level = slide_he.level_count - 1
	global working_level
	working_level = max_level - 4
	global working_dimension
	working_dimension = slide_he.level_dimensions[working_level]
	# print workingDimensions
	print "init finished, working dimension: ", working_dimension, "working level:", max_level


def get_patient_image_path(patient_no, return_type="both", file_type='.ndpi', for_split=False, is_masson=True,
                           is_he=True, slide_type='RCM'):
	"""
	:param slide_type: assign specific slide_type
	:param is_he: check he
	:param is_masson: check masson
	:param for_split: define split image mode
	:param file_type: define file format (.ndpi / .mrxs)
	:param patient_no: the number of patient in the patients[] list
	:param return_type: "both" default
	:return: the he_path and masson_path
	"""
	# patient_no = patients[patient_no]
	he_path_list = [[], []]
	masson_path_list = [[], []]
	# if is_normal:
	# 	slide__type = 'NORMAL'
	# else:
	# 	slide__type = 'RCM' if not is_hcm else 'HCM'
	if is_he:
		he_patient_no = he_patients[slide_type_all.index(slide_type)][patient_no]
	if is_masson:
		masson_patient_no = masson_patients[slide_type_all.index(slide_type)][patient_no]
	for i in xrange(1, 7):
		if is_he:
			he_img_name = he_patient_no + '-' + str(i) + file_type
			he_path_iter = img_dir + 'HE/{}'.format(slide_type) + he_patient_no + he_img_name
			if os.path.exists(img_dir + 'RGB/HE/{}'.format(slide_type) + he_patient_no):
				he_split_image_iter = img_dir + 'RGB/HE/{}'.format(
					slide_type) + he_patient_no + he_patient_no + '-' + str(i) + '.jpg'
			else:
				he_split_image_iter = img_dir + 'RGB/HE/{}'.format(slide_type) + he_patient_no + '-' + str(i) + '.jpg'
			if for_split and os.path.exists(he_path_iter):
				he_path_list[0].append(he_path_iter)
			else:
				if os.path.exists(he_split_image_iter):
					he_path_list[0].append(he_path_iter)
					he_path_list[1].append(he_split_image_iter)
		if is_masson:
			masson_slide_name = masson_patient_no + '-' + str(i) + file_type
			masson_path_iter = img_dir + 'MASSON/{}'.format(slide_type) + masson_patient_no + masson_slide_name
			if os.path.exists(img_dir + 'RGB/MASSON/{}'.format(slide_type) + masson_patient_no):
				masson_split_image_iter = img_dir + 'RGB/MASSON/{}'.format(
					slide_type) + masson_patient_no + masson_patient_no + '-' + str(
					i) + '.jpg'
			else:
				masson_split_image_iter = img_dir + 'RGB/MASSON/{}'.format(slide_type) + masson_patient_no.split('/')[
					1] + '-' + str(
					i) + '.jpg'
			if for_split and os.path.exists(masson_path_iter):
				masson_path_list[0].append(masson_path_iter)
			else:
				if os.path.exists(masson_split_image_iter):
					masson_path_list[0].append(masson_path_iter)
					masson_path_list[1].append(masson_split_image_iter)
	if return_type is "both":
		return he_path_list, masson_path_list
	elif return_type is "HE":
		return he_path_list
	else:
		return masson_path_list


masson_erosion_iteration_time_list = [10, 10, 15, 15, 15, 13]
he_erosion_iteration_time_list = [3, 3, 8, 3, 13, 9]  # for specifications


def get_test_tif():
	#  img_dir = './../../rcm_images/'
	test_image_dir = os.path.join(img_dir, 'TEST/nucleus')
	image_list = []
	for i in os.listdir(test_image_dir):
		if i.split('.')[1] == 'tif':
			image_list.append(os.path.join(test_image_dir, i))
	return image_list
	pass


def get_he_detect_result(image_list):
	detect_result = []
	for i in image_list:
		slide_test = openslide.open_slide(i)
		test_dimension = slide_test.dimensions
		# x, y = 21000, 21000
		x, y = 0, 0
		cardiac_cell_num_threshold = [50]
		vacuole_cell_num_threshold = [2]
		# region = np.array(slide_he.read_region((x, y), 0, (area_length, area_length)))
		region = np.array(slide_test.read_region((x, y), 0, test_dimension))
		region = cv2.cvtColor(region, cv2.COLOR_RGBA2BGR)
		hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
		detect = detect_process(region, hsv, he_patients[0], 0, he_mask_name[0],
		                        cardiac_cell_num_threshold, vacuole_cell_num_threshold, False, debug_mod=True,
		                        extract_mod=True)
		detect_result.append([i[0] for i in detect[-2:-1][0]])  # cardiac cell area
		'''
		detect : 空泡 心肌 非心肌 总面积 心肌细胞的面积和周长列表
		'''
	return detect_result
	pass


def he_test_proc():
	# print dimension
	# whole_level = 6
	# print "he_test_proc_dimension:", max_level
	slide_no = 0
	global slide_he
	# global slide_masson
	slide_he = openslide.open_slide(he_test_path[slide_no])
	# test_image_list = get_test_tif()  # [1.tif,2.tif...]
	# cardiac_res = get_he_detect_result(test_image_list)
	# all_res = reduce(lambda l1, l2: l1 + l2, cardiac_res)
	# print np.average(all_res)
	# slide_masson = openslide.open_slide(masson_path[slide_no])
	area_length = 1000
	# test_dimension = slide_he.dimensions
	test_dimension = (area_length, area_length)
	x, y = 32000, 21000
	# x, y = 0, 0
	cardiac_cell_num_threshold = [80]
	vacuole_cell_num_threshold = [1]
	# region = np.array(slide_he.read_region((x, y), 0, (area_length, area_length)))
	region = np.array(slide_he.read_region((x, y), 0, test_dimension))
	region = cv2.cvtColor(region, cv2.COLOR_RGBA2BGR)
	hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
	detect = detect_process(region, hsv, he_patients[0], slide_no, he_mask_name[0],
	                        cardiac_cell_num_threshold, vacuole_cell_num_threshold, False, debug_mod=True)
	detect_cardiac_area_res = [i[0] for i in detect[-2:-1][0]]
	'''
	detect : 空泡 心肌 非心肌 总面积 心肌细胞的面积和周长列表
	'''
	# firstmask, secondmask, thirdmask, othermask, rcm_thickening = edit_area(6, slide_he, he_erosion_iteration_time_list,
	#                                                                         masson_erosion_iteration_time_list,
	#                                                                         slide_no,
	#                                                                         is_masson=False)
	# write_test_img(is_masson=True)
	pass


def write_test_img(path, saved_img_level, is_masson=False):
	if is_masson is False:
		# path = he_test_path
		img_dir_path = './../test_images/HE/'
	else:
		# path = masson_test_path
		img_dir_path = './../test_images/MASSON/'
	for i in path:
		slide_iter = openslide.open_slide(i)
		try:
			whole_dimension = slide_iter.level_dimensions[saved_img_level]
		except:
			print 'slide {} corrupt'.format(i)
			continue
		region = np.array((slide_iter.read_region((0, 0), saved_img_level, whole_dimension)))
		region = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
		# cv2.imshow(i, region)
		img_path_iter = img_dir_path + i.split('/')[-2]
		if not os.path.exists(img_path_iter):
			os.mkdir(img_path_iter)
		cv2.imwrite(img_path_iter + '/' + i.split('/')[-1].split('.')[0] + '.jpg', region)
		print 'write images' + img_path_iter + '/' + i.split('/')[-1].split('.')[0] + '.jpg'


# whole_img = slide.read_region((0, 0), 0, dimension)

# print firstmask
he_mask_name = ['Endocardium', 'Midcardium', 'Epicardium', 'Heart_trabe', 'Whole']


def try_he_proc(he_task_list):
	try:
		he_proc(he_task_list)
	except BaseException, e:
		print e
		print he_task_list


def he_proc(he_task_list):
	he_slide_no, he_slide_path, patient_id, set_hand_drawn, hand_drawn_img, server, slide_type = he_task_list
	"""
	:param patient_id: id of patient
	:param hand_drawn_img: set if it's hand_drawn
	:param set_hand_drawn: hand_drawn_img path
	:param he_slide_path: path of he slide
	:param he_slide_no: the slide_no of a patient
	:return: the whole_result_list of this slide will be saved
	"""
	he_proc_start_time = time()
	he_whole_res = []
	he_proc_iter = [0, 0, 0, [0, 0], []]
	# he_slide_no = 0
	mask_level = 6
	slide_processed = openslide.open_slide(he_slide_path)
	# slide_dimension = slide_processed.dimensions
	firstmask, secondmask, thirdmask, othermask, rcm_thickening = edit_area(mask_level, slide_processed,
	                                                                        he_erosion_iteration_time_list,
	                                                                        masson_erosion_iteration_time_list,
	                                                                        patient_id=patient_id,
	                                                                        slide_no=he_slide_no,
	                                                                        hand_drawn=set_hand_drawn,
	                                                                        image_path=hand_drawn_img, server=server,
	                                                                        slide_type=slide_type)
	print '{} mask read done'.format(he_slide_no)
	global he_mask_name
	areas = [firstmask, secondmask, thirdmask, othermask]
	magnify = pow(2, mask_level)
	area_length = 1000
	# i = 0
	he_max_dimension = slide_processed.dimensions
	print "dimension working on:", he_max_dimension[1], he_max_dimension[0]
	pixels = he_max_dimension[1] * he_max_dimension[0]
	for a in xrange(len(areas)):
		if areas[a].__len__():
			cardiac_cell_num_threshold = [80]
			vacuole_cell_num_threshold = [2]
			for y in range(0, he_max_dimension[1] - area_length, area_length):
				for x in range(0, he_max_dimension[0] - area_length, area_length):
					# if whole_img[x * magnify + 500][y * magnify + 500] != 0:
					if areas[a][int((y + area_length / 2) / magnify)][int((x + area_length / 2) / magnify)] != 0:
						# 证明这个像素点在对应的Mask里面
						print str(he_patients[slide_type_all.index(slide_type)][patient_id]).split('/')[
							      1] + "({})".format(patient_id) + " HE: " + str(
							he_slide_no) + ' ' + he_mask_name[
							      a] + ": " + '{:.4f}%'.format(float(y * he_max_dimension[0] + x) / pixels * 100)
						# print x, y
						region = np.array(slide_processed.read_region((x, y), 0, (area_length, area_length)))
						region = cv2.cvtColor(region, cv2.COLOR_RGBA2BGR)
						hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
						detect = detect_process(region, hsv, he_patients[slide_type_all.index(slide_type)][patient_id], he_slide_no, he_mask_name[a],
						                        cardiac_cell_num_threshold, vacuole_cell_num_threshold, False)
						he_proc_iter[0] += (detect[0])  # 空泡
						he_proc_iter[1] += (detect[1])  # 心肌
						he_proc_iter[2] += (detect[2])  # 非心肌
						he_proc_iter[3][0] += (detect[3])  # 总面积
						he_proc_iter[4].append(detect[4])  # 心肌细胞的[area, perimeter]
		# if cardiac_cell_num_threshold > 0:
		# 	cardiac_cell_num_threshold -= 1
		else:
			print "area is none"
		# he_proc_iter[5].append(detect[5])  # 空泡的[area] 暂时没算出来，后面算，这里填空
		he_proc_iter[3][1] = rcm_thickening
		print(he_mask_name[a] + "finished!")
		# i += 1
		he_whole_res.append(he_proc_iter)
		he_proc_iter = [0, 0, 0, [0, 0], []]  # erase the he_proc_iter var
	if not os.path.exists('HE_data'):
		os.mkdir('HE_data')
	write_file(he_whole_res,
	           'HE_data/' + str(he_patients[slide_type_all.index(slide_type)][patient_id]).split('/')[1] + '_slide' + str(
		           he_slide_no) + '_he_whole_res.txt')
	he_whole_res = []
	print "HE patient: " + str(he_patients[slide_type_all.index(slide_type)][patient_id]).split('/')[1] + ' slide no:' + str(
		he_slide_no) + " finished.Time consumed:" + str(
		time() - he_proc_start_time) + " s"


def generate_whole_res(whole_res):
	# generate whole result
	whole_area_data = [0, 0, 0, [0, 0], []]
	for j in whole_res:
		whole_area_data[0] += j[0]
		whole_area_data[1] += j[1]
		whole_area_data[2] += j[2]
		whole_area_data[3][0] += j[3][0]
		whole_area_data[3][1] = j[3][1]
		whole_area_data[4].extend(j[4])
	whole_res.append(whole_area_data)
	return whole_res


def he_statics_persistence(whole_res, slide_no, print_res=False, magnify_level=6):
	"""
	:param print_res: determine whether to print the res_list
	:param whole_res: res is a list that produced by he_proc(), which stores the statics of each mask of a slide
	:return: Calculate and store in .xls
	"""
	whole_res = generate_whole_res(whole_res)
	global he_mask_name
	whole_list_data = []
	magnify = pow(2, magnify_level)
	print len(whole_res)
	for slide_index in xrange(len(whole_res)):
		if slide_no is 3 and slide_index is 3:
			continue
		if (slide_no is 4 or slide_no is 5) and slide_index is 2:
			continue
		vacuole_num = whole_res[slide_index][0]
		cardiac_cells_num = whole_res[slide_index][1]
		non_cardiac_cells_num = whole_res[slide_index][2]
		region_whole_area = whole_res[slide_index][3][0]
		region_rcm_thickening = whole_res[slide_index][3][1][1] * magnify
		region_trabe_thickening = whole_res[slide_index][3][1][0] * magnify
		cardiac_cells_nucleus_area = []
		cardiac_cells_nucleus_perimeter = []
		for a in [j for j in whole_res[slide_index][4] if len(j)]:
			for b in a:
				cardiac_cells_nucleus_area.append(b[0])
				cardiac_cells_nucleus_perimeter.append(b[1])
		# cardiac_cells_nucleus_area = [j[0] for j in whole_res[slide_index][4]]
		# cardiac_cells_nucleus_perimeter = [j[1] for j in whole_res[slide_index][4]]
		# vacuole_area = res[slide_index][5]
		
		cardiac_cells_ratio = non_cardiac_cells_num / float(cardiac_cells_num)
		cardiac_area_num_ratio = region_whole_area / float(cardiac_cells_num)
		
		#  cardiac cell nucleus statics
		# mean
		cardiac_cells_nucleus_area_mean = np.mean(cardiac_cells_nucleus_area)
		# median
		cardiac_cells_nucleus_area_median = np.median(cardiac_cells_nucleus_area)
		# SD
		cardiac_cells_nucleus_area_sd = np.std(cardiac_cells_nucleus_area, ddof=1)
		# IQR
		cardiac_cells_nucleus_area_iqr = iqr(cardiac_cells_nucleus_area, rng=(25, 75), interpolation='midpoint')
		
		# perimeter calculation
		cardiac_cells_nucleus_perimeter_mean = np.mean(cardiac_cells_nucleus_perimeter)
		cardiac_cells_nucleus_perimeter_median = np.median(cardiac_cells_nucleus_perimeter)
		cardiac_cells_nucleus_perimeter_sd = np.std(cardiac_cells_nucleus_perimeter, ddof=1)
		cardiac_cells_nucleus_perimeter_iqr = iqr(cardiac_cells_nucleus_perimeter, rng=(25, 75),
		                                          interpolation='midpoint')
		
		# nucleus / whole_area 细胞核总数量/切片总面积
		intensity = cardiac_cells_num / float(region_whole_area)
		
		# area ratio  心肌细胞核面积占心肌细胞的面积比例
		cardiac_cells_nucleus_area_region_ratio = float(sum(cardiac_cells_nucleus_area)) / region_whole_area
		
		# vacuole calculation
		# cardiac_cells_vacuole_area_mean = np.mean(vacuole_area)
		# cardiac_cells_vacuole_area_median = np.median(vacuole_area)
		# cardiac_cells_vacuole_area_sd = np.std(vacuole_area, ddof=1)
		
		if print_res:
			print 'region: ' + he_mask_name[slide_index]
			print 'Cardiac cells num: ' + str(whole_res[slide_index][1])
			print 'vacuole cells num: ' + str(whole_res[slide_index][0])
			print 'Non-cardiac cells num: ' + str(whole_res[slide_index][2])
			print 'region area: ' + he_mask_name[slide_index] + str(whole_res[slide_index][3])
		list_data_iter = [cardiac_cells_num, non_cardiac_cells_num, cardiac_cells_ratio, cardiac_area_num_ratio,
		                  cardiac_cells_nucleus_area_mean, cardiac_cells_nucleus_area_median,
		                  cardiac_cells_nucleus_area_sd, cardiac_cells_nucleus_area_iqr,
		                  cardiac_cells_nucleus_perimeter_mean, cardiac_cells_nucleus_perimeter_median,
		                  cardiac_cells_nucleus_perimeter_sd, cardiac_cells_nucleus_perimeter_iqr,
		                  intensity,
		                  cardiac_cells_nucleus_area_region_ratio,
		                  vacuole_num,
		                  region_trabe_thickening,
		                  region_rcm_thickening]  # conform to the HE.XLS form now
		whole_list_data.append(list_data_iter)
	# write_excel('HE.xls', whole_list_data)
	return whole_list_data
	# print
	pass


# for masson proc later
cardiac_threshold = (155, 15, 46), (180, 255, 255)  # cardiac
fibrosis_threshold = (78, 20, 46), (155, 255, 255)  # fibrosis
'''
[147  13 219]
[146  16 217]
[141   8 234]
[169  11 245]
[164  13 223]
[146   9 237]
[138  11 226]
[165   2 252]
[142  12 233]
'''

masson_mask_name = ['Endocardium', 'Midcardium', 'Epicardium', 'Heart_trabe', 'Whole']

fibrosis_group = [4000, 8000, 12000, 16000, 20000, 24000, 28000, 32000]


def try_masson_proc(task_list):
	try:
		masson_proc(task_list)
	except BaseException, e:
		print e
		print task_list


def masson_proc(task_list):  # need debug and fix
	slide_no, masson_slide_path, patient_id, masson_mask_working_level, hand_drawn, \
	split_image_path, slide_type = task_list
	masson_proc_time_start = time()
	
	masson_whole_result = []
	masson_result_iter = [0, 0]
	slide_processed = openslide.open_slide(masson_slide_path)
	masson_max_dimension = slide_processed.dimensions
	pixels = masson_max_dimension[1] * masson_max_dimension[0]
	
	firstmask, secondmask, thirdmask, othermask, grey_img, hsv, rcm_thickening = edit_area(
		masson_mask_working_level, slide_processed,
		masson_erosion_iteration_time_list=masson_erosion_iteration_time_list,
		slide_no=slide_no,
		patient_id=patient_id,
		hand_drawn=hand_drawn,
		is_masson=True, image_path=split_image_path, slide_type=slide_type)
	areas = [firstmask, secondmask, thirdmask, othermask]
	# save global fibrosis image
	store_level = 4
	masson_region_slide(slide_processed, store_level,
	                    "fibrosis", masson_patients[slide_type_all.index(slide_type)][patient_id],
	                    slide_no, dimension=slide_processed.level_dimensions[store_level],
	                    threshold=fibrosis_threshold,
	                    save_image=True)
	masson_region_slide(slide_processed, store_level,
	                    "cardiac", masson_patients[slide_type_all.index(slide_type)][patient_id],
	                    slide_no, dimension=slide_processed.level_dimensions[store_level],
	                    threshold=cardiac_threshold,
	                    save_image=True)
	
	# i = 0
	# print working_level
	# working_dimensions = slide_processed.level_dimensions[masson_mask_working_level]
	# rcm_thickening =  [other_height, wall_height]
	
	masson_working_level = 1  # try 3
	second_max_dimension = slide_processed.level_dimensions[masson_working_level]
	magnify = pow(2, masson_mask_working_level) / pow(2, masson_working_level)
	# 把图片缩小了两倍，那么就要除去相应的放大倍数
	area_length = 500  # 这相比HE缩小一倍
	for a in xrange(len(areas)):
		if areas[a].__len__():
			store_remain_no = [100000, 37000]
			for y in range(0, second_max_dimension[1] - area_length, area_length):
				for x in range(0, second_max_dimension[0] - area_length, area_length):
					# if area[int((y + area_length / 2) / magnify)][int((x + area_length / 2) / magnify)] != 0:
					if areas[a][int((y + area_length / 2) / magnify)][int((x + area_length / 2) / magnify)] != 0:
						# print x, y
						# print str(masson_patients[patient_id].split('/')[1]) + " MASSON: " + str(slide_no) + " " + \
						#       masson_mask_name[
						# 	      a] + ": " + '{:.4f}%'.format(float(y * masson_max_dimension[0] + x) / pixels * 100)
						_, cardiac_area = masson_region_slide(slide_processed, masson_working_level, "cardiac",
						                                      masson_patients[slide_type_all.index(slide_type)][
							                                      patient_id],
						                                      slide_no, masson_mask_name[a], store_remain_no,
						                                      cardiac_threshold,
						                                      (int(x * pow(2, masson_working_level)),
						                                       int(y * pow(2, masson_working_level))),
						                                      is_debug=False,
						                                      dimension=(area_length, area_length))
						_, fibrosis_area = masson_region_slide(slide_processed, masson_working_level, "fibrosis",
						                                       masson_patients[slide_type_all.index(slide_type)][
							                                       patient_id],
						                                       slide_no, masson_mask_name[a], store_remain_no,
						                                       fibrosis_threshold,
						                                       (int(x * pow(2, masson_working_level)),
						                                        int(y * pow(2, masson_working_level))),
						                                       is_debug=False,
						                                       dimension=(area_length, area_length))
						# if store_remain_no:
						# 	store_remain_no -= 1
						masson_result_iter[0] += cardiac_area * (magnify ** 2)
						masson_result_iter[1] += fibrosis_area * (magnify ** 2)
		# statics should be simulated at max_level
		else:
			print "area is none"
		masson_whole_result.append(masson_result_iter)
		masson_result_iter = [0, 0]
		print masson_patients[slide_type_all.index(slide_type)][patient_id] + " " + masson_mask_name[
			a] + " finished " + "time consumed now: " + str(time() - masson_proc_time_start) + "s"
	# i += 1
	# The statics for storage should be the result at max_level : 0
	#####################################################################
	# fibrosis
	print masson_patients[slide_type_all.index(slide_type)][patient_id] + " Dealing with fibrosis now"
	fibrosis_time = time()
	fibrosis_level = slide_processed.level_count - 5
	fibrosis_img = fibrosis(slide_processed, fibrosis_level)
	labels = measure.label(fibrosis_img, connectivity=2)
	number = labels.max() + 1
	total_fibrosis_block = []
	for x in range(1, number):
		# j = np.zeros((len(fibrosis_img), len(fibrosis_img[0])), np.uint8)
		# j[labels == x] = 255
		total_fibrosis_block.append(np.count_nonzero(labels == x) * (pow(2, fibrosis_level) ** 2))
		if x % 1000 == 0:
			print "patient:{} slide:{} fibrosis process:({}/{}) time_consumed:{:.4f}".format(
				masson_patients[slide_type_all.index(slide_type)][patient_id].split('/')[1],
				slide_no,
				x, number, (time() - fibrosis_time))
	print "fibrosis finished. Time consumed:" + str(time() - fibrosis_time)
	plt.cla()
	plt.hist(total_fibrosis_block, fibrosis_group, histtype='bar', rwidth=0.8)
	plt.legend()
	plt.xlabel('fibrosis plaques area distribution')
	plt.ylabel('number')
	plt.title('fibrosis plaques hist')
	plt.savefig(
		'MASSON_image' + str(masson_patients[slide_type_all.index(slide_type)][patient_id]) + '/fibrosis/slide_' + str(
			slide_no) + '_fibrosisPlaques.png',
		format='png')
	fibrosis_block_sum = int(np.sum(total_fibrosis_block))
	fibrosis_block_median = int(np.median(total_fibrosis_block))
	fibrosis_block_mean = int(np.mean(total_fibrosis_block))
	fibrosis_block_sd = int(np.std(total_fibrosis_block, ddof=1))
	fibrosis_block_info = [fibrosis_block_sum, fibrosis_block_median, fibrosis_block_mean, fibrosis_block_sd]
	####################################################################################
	masson_whole_result.append(fibrosis_block_info)  # fibrosis statics append
	masson_whole_result.append(list(magnify * np.array(rcm_thickening)))  # [other_height, wall_height]
	if not os.path.exists('MASSON_data'):
		os.mkdir('MASSON_data')
	write_file(masson_whole_result,
	           'MASSON_data/' + str(masson_patients[slide_type_all.index(slide_type)][patient_id]).split('/')[
		           1] + '_slide' + str(
		           slide_no) + '_masson_whole_res.txt')
	write_file(total_fibrosis_block,
	           'MASSON_fibrosis_data/' + str(masson_patients[slide_type_all.index(slide_type)][patient_id]).split('/')[
		           1] + '_slide' + str(
		           slide_no) + '_total_fibrosis_block.txt')
	masson_whole_result = []
	print "masson patient: " + str(masson_patients[slide_type_all.index(slide_type)][patient_id]).split('/')[
		1] + ' slide_processed ' + str(slide_no) + " finished, time consumed: " + str(
		time() - masson_proc_time_start) + " s"
	pass


def masson_persist(whole_res, slide_no, print_res=False):
	# masson persist
	whole_list_data = []
	for i in whole_res:
		for j in i:
			whole_list_data.append(j)
	
	return whole_list_data
	pass


def masson_test_proc(masson_working_level=6):
	# global slide_he
	# global slide_masson
	# print 'working level', masson_working_level
	# working_dimension = slide_masson.level_dimensions[masson_working_level]
	
	# cardiac_threshold = (155, 140, 50), (175, 230, 255)  # cardiac
	# fibrosis_threshold = (90, 20, 20), (140, 255, 255)  # fibrosis
	
	# hsv = []
	# rgb_img = []
	
	def pure_test():
		test_level = 5
		test_dimension = slide_masson.level_dimensions[test_level]
		coord = (22000, 22000)
		region = np.array(slide_masson.read_region(coord, test_level, (1000, 1000)))
		print 'test_dimension:' + str(test_dimension)
		# print "relative coordinate:" + str(coord[0]/test_dimension[0]) + ' ' + str(coord[1]/test_dimension[1])
		r, g, b, a = cv2.split(region)
		bgr_img = cv2.merge((b, g, r))
		gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
		hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
		res_fibrosis_hsv = cv2.inRange(hsv, fibrosis_threshold[0],
		                               fibrosis_threshold[1])  # s 50-255 in paper fibrosis
		res_cardiac_hsv = cv2.inRange(hsv, cardiac_threshold[0], cardiac_threshold[1])  # cardiac threshold
		t = cv2.subtract(bgr_img, cv2.cvtColor(res_fibrosis_hsv, cv2.COLOR_GRAY2BGR))
		cv2.imshow('HSV', hsv)
		cv2.imshow('black', t)
		
		def getpos(event, x, y, flags, param):
			if event == cv2.EVENT_LBUTTONDOWN:
				print(t[y, x])
		
		# cv2.imshow('res_cardiac_HSV', res_cardiac_hsv)
		# cv2.imshow('res_fibrosis_hsv', res_fibrosis_hsv)
		# cv2.imshow('rgb_masson', bgr_img)
		cv2.setMouseCallback('black', getpos)
		
		cv2.waitKey(0)
	
	pure_test()
	
	pass


def slide_proc(arg_list):
	patient_id, start, end, he, masson, set_hand_drawn, server, file_type, slide_type = arg_list
	# global he_test_path, masson_test_path
	he_slide_path, masson_slide_path = get_patient_image_path(patient_id, file_type=file_type, is_he=he,
	                                                          is_masson=masson,
	                                                          slide_type=slide_type)  # patient's image path
	for slide_no in xrange(start, end):
		if he:
			processed_index_he = 0
			try:
				for split_path in he_slide_path[1]:
					if int(split_path[-5]) == slide_no + 1:
						processed_index_he = he_slide_path[1].index(split_path)
						he_arg_list = [slide_no, he_slide_path[0][processed_index_he], patient_id, set_hand_drawn,
						               split_path if set_hand_drawn else None, server, slide_type]
						he_proc(he_arg_list)
				continue
			except BaseException, e:
				print e.message
				with open('he_error_slide_log.txt', 'a') as f:
					f.writelines(he_slide_path[0][processed_index_he] + '：' + e.message + '\n')
				continue
		if masson:
			processed_index_masson = 0
			try:
				for split_path in masson_slide_path[1]:
					if int(split_path[-5]) == slide_no + 1:
						processed_index_masson = masson_slide_path[1].index(split_path)
						masson_arg_list = [slide_no, masson_slide_path[0][processed_index_masson], patient_id,
						                   6, set_hand_drawn, split_path if set_hand_drawn else None, slide_type]
						masson_proc(masson_arg_list)
			except BaseException, e:
				print e.message
				with open('masson_error_slide_log.txt', 'a') as f:
					f.writelines(masson_slide_path[0][processed_index_masson] + '：' + e.message + '\n')
					continue


def masson_data_process(whole_res):
	new_res = []
	fibrosis_whole_area = 0
	cardiac_whole_area = 0
	tmp_s = 0
	for x in xrange(4):
		cardiac_whole_area += whole_res[x * 2 + 0]
		fibrosis_whole_area += whole_res[x * 2 + 1]
		new_res.append(whole_res[x * 2 + 0])
		new_res.append(whole_res[x * 2 + 1])
		tmp_s = whole_res[x * 2 + 1] + whole_res[x * 2 + 0]
		if tmp_s:
			new_res.append(whole_res[x * 2 + 0] / tmp_s)
			new_res.append(whole_res[x * 2 + 1] / tmp_s)
		else:
			new_res.append(whole_res[x * 2 + 0])
			new_res.append(whole_res[x * 2 + 1])
	tmp_s = fibrosis_whole_area + cardiac_whole_area
	new_res.append(cardiac_whole_area / tmp_s)
	new_res.append(fibrosis_whole_area / tmp_s)
	new_res += whole_res[-6:]
	return new_res
	pass


def xls_persist_slide(file_name, slide_type, start_row=-1, set_start_row=False):  # save one slide into .xls
	patient_no = (file_name.split('_')[0])
	slide_no = int(file_name.split('_')[1][-1])
	if slide_type is "HE":  # HE
		# file_name = 'HE_data/28330_slide0_he_whole_res.txt'
		file_name = 'HE_data/' + file_name
		res = read_file(file_name, print_file=False)
		whole_list_data = he_statics_persistence(res, slide_no)
		if set_start_row:
			write_excel('HE.xls', whole_list_data, patient_no=patient_no, slide_no=slide_no, start_row=start_row)
		else:
			write_excel('HE.xls', whole_list_data, patient_no=patient_no, slide_no=slide_no)
		print 'xls_persist() for HE: patient_no ' + str(patient_no) + ' slide_no ' + str(slide_no) + " finished"
	elif slide_type is "MASSON":
		# masson persist
		file_name = 'MASSON_data/' + file_name
		res = read_file(file_name, print_file=False)
		whole_list_data = masson_persist(res, slide_no)
		whole_list_data = masson_data_process(whole_list_data)
		if set_start_row:
			write_excel('MASSON.xls', whole_list_data, patient_no, slide_no, start_row)
		else:
			write_excel('MASSON.xls', whole_list_data, patient_no, slide_no)
		print 'xls_persist() for MASSON: patient_no ' + str(patient_no) + ' slide_no ' + str(slide_no) + " finished"
		pass


if __name__ == '__main__':
	# in rcm_main_proc.py
	pass
