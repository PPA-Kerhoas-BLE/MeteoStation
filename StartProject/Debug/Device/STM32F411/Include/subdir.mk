################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Device/STM32F411/Include/stm32f4xx_nucleo.c 

OBJS += \
./Device/STM32F411/Include/stm32f4xx_nucleo.o 

C_DEPS += \
./Device/STM32F411/Include/stm32f4xx_nucleo.d 


# Each subdirectory must supply rules for building sources it contributes
Device/STM32F411/Include/%.o: ../Device/STM32F411/Include/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: Cross GCC Compiler'
	gcc -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


