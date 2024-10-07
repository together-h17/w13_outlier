# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 09:49:06 2024

@author: ae133
"""

import geopandas as gpd
import numpy as np
from scipy import stats
import glob
import os
import tqdm

points_path = r"D:\Users\ae133\Desktop\python project\w12_DEM轉LOD1屋頂面\step1_outlier\output"
polygons_path = r"P:\13049-113年度三維建物模型更新及精進採購案\Working\士哲提供QGIS"
output_path = r"D:\Users\ae133\Desktop\python project\w12_DEM轉LOD1屋頂面\step2_decide_roof_height\output"


pt_files = glob.glob(points_path + "\\point_selected_STD_*.shp")
progress = tqdm.tqdm(total = len(pt_files), position = 0, leave = True)
for pt_file in pt_files:
    
    # 提取檔案圖幅編號
    file_id = os.path.basename(pt_file).split("_")[-1].split(".")[0]
    
    points_gdf = gpd.read_file(pt_file)
    polygons_gdf = gpd.read_file(polygons_path + "\\" +  file_id + ".shp")
    
    # 強制轉換資料型態，避免最後匹配錯誤:(
    polygons_gdf['BUILD_ID'] = polygons_gdf['BUILD_ID'].astype(str)
    points_gdf['BUILD_ID'] = points_gdf['BUILD_ID'].astype(str)
    
    # 設定計算欄位
    dsm_z = 'grid_code'
    DIFF = 3
    
    # 新增欄位紀錄屋頂高度
    polygons_gdf['roof_h'] = 0.0
    
    # 按 BUILD_ID 分組
    grouped = points_gdf.groupby('BUILD_ID')
    
    for name, group in grouped:
        diff = group[dsm_z].max() - group[dsm_z].min()
        
        #判斷斜屋頂
        if diff > DIFF:
            roof_height = group[dsm_z].min()
        else:
            #解決眾數問題
            rounded = np.round(group[dsm_z])
            mode, _ = stats.mode(rounded, keepdims=False)       # 註：_ 表示不需要這個變數，一般mode會吐出眾數及出現次數
            roof_height = float(mode)                           # keepdims因應scipy設置
            
        # 寫入高度進gdf
        polygons_gdf.loc[polygons_gdf['BUILD_ID'] == name, 'roof_h'] = roof_height
        
    new_filename = f"roof_height_{file_id}.shp"
    # 將結果寫入新的 shapefile
    output_file = os.path.join(output_path, new_filename)
    # 將結果寫入新的 shapefile
    polygons_gdf.to_file(output_file)
    
    progress.update(1)
progress.close()