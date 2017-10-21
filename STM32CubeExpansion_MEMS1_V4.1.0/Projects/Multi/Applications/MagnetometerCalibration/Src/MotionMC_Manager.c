/**
  ******************************************************************************
  * @file        MotionMC_Manager.c
  * @author      MEMS Application Team
  * @version     V2.0.0
  * @date        01-May-2017
  * @brief       This file includes magnetometer calibration interface functions
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; COPYRIGHT(c) 2017 STMicroelectronics</center></h2>
  *
  * Redistribution and use in source and binary forms, with or without modification,
  * are permitted provided that the following conditions are met:
  *   1. Redistributions of source code must retain the above copyright notice,
  *      this list of conditions and the following disclaimer.
  *   2. Redistributions in binary form must reproduce the above copyright notice,
  *      this list of conditions and the following disclaimer in the documentation
  *      and/or other materials provided with the distribution.
  *   3. Neither the name of STMicroelectronics nor the names of its contributors
  *      may be used to endorse or promote products derived from this software
  *      without specific prior written permission.
  *
  * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
  * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
  * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
  * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
  * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
  * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "MotionMC_Manager.h"

/** @addtogroup MOTION_MC_Applications
  * @{
  */

/** @addtogroup MAG_CALIB
  * @{
  */

/** @addtogroup MotionMC_Manager MotionMC_Manager
  * @{
  */

/* Private typedef -----------------------------------------------------------*/

/* Exported functions prototypes ---------------------------------------------*/
// TODO: Must be implemented for each platform separately, because its implementation
//       is platform dependend. No need to call this function, library call this
//       function automatically.
char MotionMC_LoadCalFromNVM(unsigned short int datasize, unsigned int *data);

// TODO: Must be implemented for each platform separately, because its implementation
//       is platform dependend. No need to call this function, library call this
//       function automatically.
char MotionMC_SaveCalInNVM(unsigned short int datasize, unsigned int *data);



/**
  * @brief  Initialize the MotionMC engine
  * @param  sampletime period in milliseconds [ms] between the update function call
  * @param  enable enable (1) or disable (0) library
  * @retval none
  */
void MotionMC_manager_init(int sampletime, unsigned short int enable)
{
  MotionMC_Initialize(sampletime, enable);
}



/**
  * @brief  Run magnetometer calibration algorithm.
  * @param  data_in  Structure containing input data
  * @retval none
  */
void MotionMC_manager_update(MMC_Input_t *data_in)
{
  MotionMC_Update(data_in);
}



/**
  * @brief  Get the magnetometer calibration values for hard/soft iron.
  * @param  data_out  Structure containing output data
  * @retval none
  */
void MotionMC_manager_get_params(MMC_Output_t *data_out)
{
  MotionMC_GetCalParams(data_out);
}



/**
  * @brief  Get the library version
  * @param  version  Library version string (must be array of 35 char)
  * @param  length  Library version string length
  * @retval none
  */
void MotionMC_manager_get_version(char *version, int *length)
{
  *length = MotionMC_GetLibVersion(version);
}



/**
  * @brief  Do hard & soft iron calibration
  * @param  data_raw  Raw magnetometer data [mGauss]
  * @param  data_comp  Calibrated (compensated) data (hard & soft iron calibration) [mGauss]
  * @retval none
  */
void MotionMC_manager_compensate(SensorAxes_t *data_raw, SensorAxes_t *data_comp)
{
  MMC_Output_t data_out;

  MotionMC_GetCalParams(&data_out);

  float mag_raw_mG[3];
  float mag_comp_mG[3];

  mag_raw_mG[0] = data_raw->AXIS_X;
  mag_raw_mG[1] = data_raw->AXIS_Y;
  mag_raw_mG[2] = data_raw->AXIS_Z;

  /* Compensate magnetometer data */
  /* NOTE: Convert hard iron coeficients [uT] to [mGauss] */
  for (int i = 0; i < 3; i++)
  {
    mag_comp_mG[i] = 0;
    for (int j = 0; j < 3; j++)
    {
      mag_comp_mG[i] += (mag_raw_mG[j]  -  data_out.HI_Bias[j] * 10.0f)  *  data_out.SF_Matrix[i][j];
    }

    mag_comp_mG[i] += (mag_comp_mG[i] >= 0) ? 0.5f : -0.5f;
  }

  data_comp->AXIS_X = (int32_t)mag_comp_mG[0];
  data_comp->AXIS_Y = (int32_t)mag_comp_mG[1];
  data_comp->AXIS_Z = (int32_t)mag_comp_mG[2];
}



/**
  * @brief  Convert magnetometer data value from [uT] to [mGauss]
  * @param  mag_val_uT  magnetometer data value [uT]
  * @retval magnetometer data value [mGauss]
  */
int32_t mag_val_to_mGauss(float mag_val_uT)
{
  if (mag_val_uT >= 0)
  {
    return (int32_t)(mag_val_uT * 10.0f  +  0.5f);
  }

  else
  {
    return (int32_t)(mag_val_uT * 10.0f  -  0.5f);
  }
}



// TODO: Must be implemented for each platform separately, because its implementation
//       is platform dependend. No need to call this function, library call this
//       function automatically.
/**
  * @brief Load the calibration parameters from storage
  * @param dataSize  size of data
  * @param data  pointer to data
  * @retval Will return 0 the if it is sucess and 1 if it is failure
 */
char MotionMC_LoadCalFromNVM(unsigned short int datasize, unsigned int *data)
{
  return 1; /* FAILURE: Read from NVM not implemented. */
}



// TODO: Must be implemented for each platform separately, because its implementation
//       is platform dependend. No need to call this function, library call this
//       function automatically.
/**
  * @brief Save the calibration parameters in storage
  * @param dataSize  size of data
  * @param data  pointer to data
  * @retval Will return 0 the if it is sucess and 1 if it is failure
 */
char MotionMC_SaveCalInNVM(unsigned short int datasize, unsigned int *data)
{
  return 1; /* FAILURE: Write to NVM not implemented. */
}

/**
  * @}
  */

/**
  * @}
  */

/**
  * @}
  */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
