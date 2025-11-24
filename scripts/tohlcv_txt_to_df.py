# import pandas as pd
# import pyarrow.feather as feather

# def txt_to_dataframe(file_path):
#     data = []
#     with open(file_path, 'r') as file:
#         for line in file:
#             parts = line.strip().split(',')
#             if len(parts) == 6:
#                 timestamp = pd.Timestamp(parts[0])
#                 open_price = float(parts[1])
#                 high_price = float(parts[2])
#                 low_price = float(parts[3])
#                 close_price = float(parts[4])
#                 volume = int(parts[5])
#                 data.append([timestamp, open_price, high_price, low_price, close_price, volume])
    
#     column_names = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
#     df = pd.DataFrame(data, columns=column_names)
#     return df

# if __name__ == "__main__":
#     print('LET\'S GO')
#     input_file_path = "../data/spy/SPY_firstratedatacom1.txt"
#     output_dataframe = txt_to_dataframe(input_file_path)
#     feather_path = 'spy_data.feather'
#     feather.write_feather(output_dataframe, feather_path)
#     print(output_dataframe)