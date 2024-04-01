import json

class Loadcell:
    def __init__(self):
    
        try:
            with open('calibration.json', 'r') as f:
                    data = json.load(f)
                    offset = data['offset']
                    scale_ratio = data['ratio']
                    self.hx.set_offset(offset)
                    self.hx.set_scale_ratio(scale_ratio)
            print('Offset loaded from calibration.json')
        except FileNotFoundError:
            print('Calibration file not found. Please set offset again.')
            calibration = {'offset':1,'scale_ratio':1}
            with open('calibration.json', 'w') as f:
                json.dump(calibration, f, indent="\t")
                # json.dump({'offset': offset}, f, indent="\t")
            print('Offset saved to new calibration.json')

if __name__ == "__main__":
    LC = Loadcell()