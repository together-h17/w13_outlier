# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 11:18:13 2024

@author: AD200
"""

import geopandas as gpd
import numpy as np
import tqdm
import glob
import os

# 讀取 shapefile
shapefile_path = r"D:\Users\ae133\Desktop\python project\w12_DEM轉LOD1屋頂面\step1_outlier\input"
output_path = r"D:\Users\ae133\Desktop\python project\w12_DEM轉LOD1屋頂面\step1_outlier\output"



files = glob.glob(shapefile_path + "\DSM_to_point_BUILDID_*.shp")
progress = tqdm.tqdm(total = len(files), position = 0, leave = True)
for file in files: 
    gdf = gpd.read_file(file)
    
    # 假設 grid_code 是我們需要計算差異的欄位
    attribute_field = 'grid_code'
    
    # 新增欄位以存儲與平均值的差異、標準差以及離群標記
    gdf['Difference_from_Mean'] = 0.0
    gdf['STD'] = 0.0
    gdf['outlier'] = 0
    
    # 按 BUILD_ID 分組
    grouped = gdf.groupby('BUILD_ID')
    
    # 計算每個點與其 BUILD_ID 組平均值的差異、標準差以及離群標記
    for name, group in grouped:
        mean = group[attribute_field].mean()
        std_dev = group[attribute_field].std()
        
        # 計算每個點與平均值的差異
        gdf.loc[gdf['BUILD_ID'] == name, 'Difference_from_Mean'] = gdf[gdf['BUILD_ID'] == name][attribute_field] - mean
        
        # 計算每個 BUILD_ID 組的標準差
        gdf.loc[gdf['BUILD_ID'] == name, 'STD'] = std_dev
        
        # 設置離群標記
        gdf.loc[gdf['BUILD_ID'] == name, 'outlier'] = np.where(
            abs(gdf[gdf['BUILD_ID'] == name]['Difference_from_Mean']) > (3 * std_dev),
            1, 0
        )
    
    # 只留下非outlier的值   
    gdf = gdf[gdf['outlier'] != 1]
    
    #取得檔案名
    filename = os.path.basename(file)
    # 提取圖幅編號
    file_id = filename.split("_")[-1].split(".")[0]  
    # 動態生成輸出的檔名
    new_filename = f"point_selected_STD_{file_id}.shp"
    # 將結果寫入新的 shapefile
    output_file = os.path.join(output_path, new_filename)
    gdf.to_file(output_file)
    
    progress.update(1)
progress.close()