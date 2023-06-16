'''
Created on 22 march 2022

Decode for datatype Liste_Entier
'''
import string

DATA_TYPE_NAME = "Liste_Entier"
DATA_TYPE_ID = 0x51

def datatype_scan(datatype):
  if datatype == 0x02 :
    type_data = 'temperature_'
  elif datatype == 0x04 :
    type_data = 'pressionAtm_'
  elif datatype == 0x05 :
    type_data = 'AirHumi_'
  elif datatype == 0x08 :
    type_data = 'IlluminanceLux_'
  elif datatype == 0x0A :
    type_data = 'SolutionConductivity_'
  elif datatype == 0x0C :
    type_data = 'VoltageV_'
  elif datatype == 0x0E :
    type_data = 'RainAmoutMM_'
  elif datatype == 0x10 :
    type_data = 'SoilMoistureCb_'
  elif datatype == 0x12 :
    type_data = 'SolutionConductivityUSCm_'
  elif datatype == 0x13 :
    type_data = 'SolutionConductivityMSCm_'
  elif datatype == 0x14 :
    type_data = 'PressurePa_'
  elif datatype == 0x17 :
    type_data = 'WindSpeedMS_'
  elif datatype == 0x18 :
    type_data = 'WindDirectionDegN_'
  elif datatype == 0x19 :
    type_data = 'SolraIrradianceWM2_'
  elif datatype == 0x1A :
    type_data = 'RadioactivityBqM3_'
  elif datatype == 0x1C :
    type_data = 'DepthCm_'
  elif datatype == 0x1E :
    type_data = 'SoilVolumetricWaterContentPercent_'
  elif datatype == 0x20 :
    type_data = 'LevelM_'
  elif datatype == 0x21 :
    type_data = 'SolutionSpecificConductivityUSCm_'
  elif datatype == 0x22 :
    type_data = 'SolutionSpecificConductivityMSCm_'
  elif datatype == 0x26 :
    type_data = 'WindAvgSpeedMS_'
  else :
    type_data = 'Entier16_'
    
  return type_data
    
def unit_scan(datatype): 
  if datatype == 0x02 :
    unit_data = '°C'
  elif datatype == 0x04 :
    unit_data = 'hPa'
  elif datatype == 0x05 :
    unit_data = '%'
  elif datatype == 0x08 :
    unit_data = 'Lux'
  elif datatype == 0x0A :
    unit_data = 'S/cm'
  elif datatype == 0x0C :
    unit_data = 'V'
  elif datatype == 0x0E :
    unit_data = 'mm'
  elif datatype == 0x10 :
    unit_data = 'centibars'
  elif datatype == 0x12 :
    unit_data = 'uS/cm'
  elif datatype == 0x13 :
    unit_data = 'mS/cm'
  elif datatype == 0x14 :
    unit_data = 'Pa'
  elif datatype == 0x17 :
    unit_data = 'm/s'
  elif datatype == 0x18 :
    unit_data = 'Degrés'
  elif datatype == 0x19 :
    unit_data = 'W/m²'
  elif datatype == 0x1A :
    unit_data = 'Bq/m3'
  elif datatype == 0x1C :
    unit_data = 'cm'
  elif datatype == 0x1E :
    unit_data = '%'
  elif datatype == 0x20 :
    unit_data = 'mètre'
  elif datatype == 0x21 :
    unit_data = 'uS/cm'
  elif datatype == 0x22 :
    unit_data = 'Ms/cm'
  elif datatype == 0x26 :
    unit_data = 'm/s'
  else :
    unit_data = 'Entier16_'
    
  return unit_data

def decode_payload(payload,
           channel,
           res,
           frame_global_values,
           channel_gloabl_values):

  Nb_value = payload[0] | (payload[1] << 8)
  payload = payload[2:]

  i=0
  while i < Nb_value:
    datatype_test = payload[0]
    payload = payload[1:]
    value = payload[0] | (payload[1] << 8)
    payload = payload[2:]
    
    type_data = datatype_scan(datatype_test)
    unit = unit_scan(datatype_test)
    
    res[type_data + str(i)]      = value
    res[type_data + str(i) + '-unit'] = unit
    
    i=i+1
  
  return payload

    