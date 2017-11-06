PATH_TO_BIN = /local/sdk_elec/gcc-arm-none-eabi-5_2-2015q4/bin/


TARGET  = $(PATH_TO_BIN)arm-none-eabi-

CC      = $(TARGET)gcc
OBJCOPY = $(TARGET)objcopy
AS      = $(TARGET)gcc -x assembler-with-cpp -c
SIZE    = $(TARGET)size
OBJDUMP = $(TARGET)objdump

PROJECT_NAME = template

PROJECT_SRC = .
STM_SRC = /STM32F4xx_HAL_Driver/Sources/


vpath %.c $(PROJECT_SRC)
vpath %.c $(STM_SRC)


#EXT_SRCS = stm32f4xx_hal.c
#EXT_SRCS += stm32f4xx_hal_rcc.c
#EXT_SRCS += stm32f4xx_hal_gpio.c
#EXT_SRCS += stm32f4xx_hal_cortex.c
#EXT_SRCS += stm32f4xx_hal_pcd.c
#EXT_SRCS += stm32f4xx_hal_pcd_ex.c
#EXT_SRCS += stm32f4xx_hal_uart.c
#EXT_SRCS += stm32f4xx_hal_usart.c
#EXT_SRCS += stm32f4xx_hal_dma.c
#EXT_SRCS += stm32f4xx_hal_tim.c
#EXT_SRCS += stm32f4xx_hal_tim_ex.c
#EXT_SRCS += stm32f4xx_hal_adc.c
#EXT_SRCS += stm32f4xx_hal_adc_ex.c
#EXT_SRCS += stm32f4xx_hal_spi.c
#EXT_SRCS += stm32f4xx_hal_i2c.c
SRCS =      Main/Includes/main.c

SRCS +=  Device/STM32F411/Include/Source_Startup/Templates/gcc/startup_stm32f411xe.s
SRCS +=  Device/STM32F411/Include/stm32f4xx_nucleo.c

#SRCS += src/stm32f4xx_hal_msp.c
#SRCS += src/stm32f4xx_it.c
#SRCS += src/system_stm32f4xx.c
#SRCS += src/newlib_stubs.c
#SRCS += src/SystemClock.c
#SRCS += src/tickTimer.c

#SRCS += src/drv/drv_i2c.c
#SRCS += src/drv/drv_uart.c
#SRCS += src/drv/drv_spi.c
#SRCS += src/drv/drv_gpio.c


EXT_OBJ = $(EXT_SRCS:.c=.o)
INC_DIRS +=  Device/
INC_DIRS +=  STM32F4xx_HAL_Driver/Inc/
INC_DIRS +=  STM32F4xx_HAL_Driver/Src/
INC_DIRS +=  Device/STM32F411/
INC_DIRS +=  Device/CMSIS/IncludeARM/
#INC_DIRS +=  Device/BSP/STM32F4xx-Nucleo/




INCLUDE = $(addprefix -I,$(INC_DIRS))

DEFS = -DSTM32F411xE

CFLAGS  = -ggdb -O0
CFLAGS += -mlittle-endian -mthumb -mcpu=cortex-m4 -mthumb-interwork -Wl,--gc-sections -mfpu=fpv4-sp-d16 -mfloat-abi=hard -fsingle-precision-constant

WFLAGS += -Wall -Wextra -Warray-bounds -Wno-unused-parameter

LFLAGS = -TDevice/gcc.ld -mfloat-abi=hard -lc -lgcc -lgcov -lm -Wl,-Map=$@.map



.PHONY: all
all: $(PROJECT_NAME)

.PHONY: $(PROJECT_NAME)
$(PROJECT_NAME): $(PROJECT_NAME).elf

$(PROJECT_NAME).elf: $(SRCS) $(EXT_OBJ)
	$(CC) $(INCLUDE) $(DEFS) $(CFLAGS) $(WFLAGS) $(LFLAGS) $^ -o $@
	$(OBJCOPY) -O ihex $(PROJECT_NAME).elf   $(PROJECT_NAME).hex
	$(OBJCOPY) -O binary $(PROJECT_NAME).elf $(PROJECT_NAME).bin

%.o: %.c
	$(CC) -c -o $@ $(INCLUDE) $(DEFS) $(CFLAGS) $^

clean:
	rm -f *.o $(PROJECT_NAME).elf $(PROJECT_NAME).hex $(PROJECT_NAME).bin $(PROJECT_NAME).map

	
	
