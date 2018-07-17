# dependencies
import scipy
import pandas as pd
import numpy as np
from plotnine import *
from plotnine.data import *

# define cost functions
def cost_centroid_dist(i, j):
    return((j.centroid_x - i.centroid_x)**2 + (j.centroid_y - i.centroid_y)**2)

# if distance > 25, then make the cost = infinity
def cost_max_dist(i,j):
    if np.sqrt((j.centroid_x - i.centroid_x)**2 + (j.centroid_y - i.centroid_y)**2) > 25:
        return(9999999999999999999)
    else:
        return(0)

def total_cost(i,j):
    return(cost_centroid_dist(i,j) + cost_max_dist(i,j))

## define cost_matrix_creator
    # INPUTS: dataframe of values from frame a (contains objects i); dataframe of values from frame b (contains objects j); cost_function
    # if sort_objects = True, object_no in each frame will be sorted. It is crucial they are sorted for later experiments
    # OUTPUTS: cost matrix, with column index values = objects j from frame_b and row index values = objects i from frame_a
def cost_matrix_creator(frame_a,frame_b, cost_func = total_cost, sort_objects = True):

    # sort inputs by object, if required
    if sort_objects:
        frame_a = frame_a.sort_values('object_no')
        frame_b = frame_b.sort_values('object_no')

    # function that parses through frame_a for one object in frame_b
    def parse_frame_a(j, frame_a):
        output = frame_a.apply(cost_func, axis = 1, j = j)
        return(frame_a.apply(cost_func, axis = 1, j = j))

    # for each object in frame_b, apply the parse_frame_a function
    cost_matrix = frame_b.apply(parse_frame_a, axis = 1, frame_a = frame_a)
    cost_matrix.index = frame_b.object_no
    cost_matrix.index.names = ['b_obj']
    cost_matrix.columns = frame_a.object_no
    cost_matrix.columns.names = ['a_obj']
    return(cost_matrix)

## define label_tracking
    #INPUTS: frame_a, frame_b, cost_matrix
    #OUTPUT: new dataframe with tracking_ids
        # if frame_a already has tracking_ids, these will be used as reference
        # else, frame_a object nums will serve as initializing tracking ids
def label_tracking(frame_a,frame_b,cost_matrix, return_frame_a = False):
    # initialize frame_a tracking ids, if necessary
    if 'tracking_id' not in frame_a:
        frame_a['tracking_id'] = frame_a['object_no']

    # use scipy optimize to solve cost matrix
    # row_ind = row indices of the cost matrix that
    row_ind, col_ind = scipy.optimize.linear_sum_assignment(cost_matrix_creator(frame_a,frame_b))

    # iterate through row and column indicies to pick out i-j relationships
    j_objs = cost_matrix.index[row_ind]
    i_objs = cost_matrix.columns[col_ind]
    obj_pairs = pd.DataFrame({'obj_i':i_objs, 'obj_j':j_objs})

    ## use tracking id from frame_a to give tracking ids to frame_b
    # merge frame_a tracking id onto obj_pairs for reference
    obj_pairs = obj_pairs.merge(frame_a.loc[:,['object_no','tracking_id']], left_on='obj_i', right_on = 'object_no')
    # define frame_b tracking id
    frame_b = frame_b.merge(obj_pairs.loc[:,['obj_j', 'tracking_id']], left_on = 'object_no', right_on = 'obj_j')

    # remove the extra obj_j column
    frame_b = frame_b.drop('obj_j', axis = 1)

    if return_frame_a:
        return(frame_a)
    else:
        return(frame_b)

## define iterate_tracking
    # INPUTS:
        # df = dataframe with frame_ids, object_no, and all values needed for cost function
        # cost_func = cost function
        # frame_ids = name of frame_ids column (default = 'stack_num')
        # object_ids = name of obejct_no column (default = 'object_no')
    # OUTPUTS:
        # dataframe containing tracking ids

def iterate_tracking(df, cost_func, frame_ids = 'stack_num', object_ids = 'object_no'):

    output_df_list = []

    # iterate through frames from frame = 1 to frame = n - 1.
    for frame in range(1, max(df[frame_ids]) - 1):
        # for the first iteration, frame_a = 1 with tracking_id = object_id. For the rest, frame_b = frame_a (do this to keep tracking ids)
        if frame == 1:
            frame_a = df[df[frame_ids] == frame]
            frame_a['tracking_id'] = frame_a[object_ids]
            output_df_list.append(frame_a)
        else:
            frame_a = frame_b

        # for all iterations, frame_b = the current frame, plus one
        frame_b = df[df[frame_ids] == frame + 1]

        # create cost matrix for the frame pair
        cost_matrix = cost_matrix_creator(frame_a, frame_b, cost_func = cost_func)

        # solve cost matrix and output new frame_b with tracking id
        frame_b = label_tracking(frame_a,frame_b,cost_matrix, return_frame_a = False)
        # append frame_b to cost_matrix
        output_df_list.append(frame_b)

    # concatenate new dataframe and output
    output = pd.concat(output_df_list, ignore_index = True)
    return(output)
