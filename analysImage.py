from PIL import Image
import pyocr
from collections import Counter
import numpy as np
import pandas as pd
import os

TESSDATA_PATH="C:\Program Files\Tesseract-OCR\tessdata"
os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH

def analyze_pixel_row_categories(score_bar_img,tolerance=30):
    """
    指定された行のピクセルを特定のカテゴリーに分類して分析する
    
    Parameters:
    score_bar_img: スコアバー画像
    row_number: 分析する行番号
    """
    # 検索対象の色を定義
    target_colors = {
        'Vo': (242, 53, 132),
        'None': (255, 255, 255),
        'Da': (28, 133, 237),
        'Vi': (247, 177, 46)
    }
    
    img_array = np.array(score_bar_img)
    
    # 指定行のピクセルを取得
    row_pixels = img_array[0]
    
    # 各色のカウントを保持する辞書
    color_counts = {name: 0 for name in target_colors.keys()}
    
    # 各ピクセルについて色を判定
    for pixel in row_pixels:
        for color_name, target_rgb in target_colors.items():
            # RGB値の差を計算
            diff = np.abs(pixel - target_rgb)
            
            # すべての色チャンネルが許容誤差内なら、その色としてカウント
            if np.all(diff <= tolerance):
                color_counts[color_name] += 1
    
    # DataFrameに変換
    df = pd.DataFrame({
        'Category': list(color_counts.keys()),
        'rgb_value': [f'RGB{target_colors[name]}' for name in color_counts.keys()],
        'pixel_count': list(color_counts.values())
    })
    
    return df.reset_index(drop=True)

def str_to_positive_integer(number_str):
    """
    数値を表す文字列を0以上の整数に変換する関数
    小数点がある場合は、小数点以下の桁数分10をかけて整数にする
    
    Args:
        number_str (str): 数値を表す文字列
    
    Returns:
        int: 0以上の整数
    """

    if '.' in number_str:
        decimal_places = len(number_str.split('.')[1])
        # 小数点を除去して整数に変換
        result = int(number_str.replace('.', ''))
    else:
        result = int(number_str)
    
    return result

def score_ocr(score_img):
  tools = pyocr.get_available_tools()
  tool = tools[0]

  return tool.image_to_string(score_img, lang='eng', builder=pyocr.builders.DigitBuilder(tesseract_layout=6))

def calculate_results(data, total_reference):
    df = data.copy()
    df = df[df['Category'] != 'None'].copy()
    df['pixel_count'] = df['pixel_count'].astype(float)
    
    # 最小の2つのカテゴリーを特定
    min_categories = df.sort_values('pixel_count')[:2]
    
    # 最小の2つのカテゴリーに2を加算、それ以外に1を加算
    df.loc[df['Category'].isin(min_categories['Category']), 'pixel_count'] += 2
    df.loc[~df['Category'].isin(min_categories['Category']), 'pixel_count'] += 1
    
    # 各カテゴリーの更新後のピクセル数を取得
    vo_pixels = df.loc[df['Category'] == 'Vo', 'pixel_count'].iloc[0]
    da_pixels = df.loc[df['Category'] == 'Da', 'pixel_count'].iloc[0]
    vi_pixels = df.loc[df['Category'] == 'Vi', 'pixel_count'].iloc[0]
    
    # 合計を計算（スケーリング用）
    current_total = vo_pixels + da_pixels + vi_pixels
    
    # スケーリング係数を計算
    scaling_factor = total_reference / current_total
    
    # 最終結果を計算
    result1 = int(round(vo_pixels * scaling_factor))
    result2 = int(round(da_pixels * scaling_factor))
    result3 = int(round(vi_pixels * scaling_factor))
    
    return result1, result2, result3


def main(img):
  # TODO: 固定値で画像の読み取りをしているので、画面サイズが変わると動作しない
  status_bar_img= img.crop((453, 408, 720, 409))
  score_img= img.crop((266, 395, 450, 427))

  score_ocr_result = score_ocr(score_img)
  score = str_to_positive_integer(score_ocr_result)

  data = analyze_pixel_row_categories(status_bar_img)

  result1, result2, result3 = calculate_results(data, score)

  return result1, result2, result3


if __name__ == "__main__":
    img_1 = Image.open("./images/MuMu12-20250115-155119.png").convert('RGB')
    result1, result2, result3 = main(img_1)
    print(result1, result2, result3)
