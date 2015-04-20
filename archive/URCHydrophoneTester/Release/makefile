################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../makefile.init

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
ifneq ($(strip $(ASM_DEPS)),)
-include $(ASM_DEPS)
endif
ifneq ($(strip $(S_DEPS)),)
-include $(S_DEPS)
endif
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 
LSS += \
pr02-URCHydrophoneTester.lss \

FLASH_IMAGE += \
pr02-URCHydrophoneTester.hex \

EEPROM_IMAGE += \
pr02-URCHydrophoneTester.eep \

SIZEDUMMY += \
sizedummy \


# All Target
all: pr02-URCHydrophoneTester.elf secondary-outputs

# Tool invocations
pr02-URCHydrophoneTester.elf: $(OBJS) $(USER_OBJS)
	@echo 'Building target: $@'
	@echo 'Invoking: AVR C Linker'
	avr-gcc -Wl,-Map,pr02-URCHydrophoneTester.map -mmcu=atmega328p -o "pr02-URCHydrophoneTester.elf" $(OBJS) $(USER_OBJS) $(LIBS)
	@echo 'Finished building target: $@'
	@echo ' '

pr02-URCHydrophoneTester.lss: pr02-URCHydrophoneTester.elf
	@echo 'Invoking: AVR Create Extended Listing'
	-avr-objdump -h -S pr02-URCHydrophoneTester.elf  >"pr02-URCHydrophoneTester.lss"
	@echo 'Finished building: $@'
	@echo ' '

pr02-URCHydrophoneTester.hex: pr02-URCHydrophoneTester.elf
	@echo 'Create Flash image (ihex format)'
	-avr-objcopy -R .eeprom -R .fuse -R .lock -R .signature -O ihex pr02-URCHydrophoneTester.elf  "pr02-URCHydrophoneTester.hex"
	@echo 'Finished building: $@'
	@echo ' '

pr02-URCHydrophoneTester.eep: pr02-URCHydrophoneTester.elf
	@echo 'Create eeprom image (ihex format)'
	-avr-objcopy -j .eeprom --no-change-warnings --change-section-lma .eeprom=0 -O ihex pr02-URCHydrophoneTester.elf  "pr02-URCHydrophoneTester.eep"
	@echo 'Finished building: $@'
	@echo ' '

sizedummy: pr02-URCHydrophoneTester.elf
	@echo 'Invoking: Print Size'
	-avr-size --format=avr --mcu=atmega328p pr02-URCHydrophoneTester.elf
	@echo 'Finished building: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) $(OBJS)$(C_DEPS)$(ASM_DEPS)$(EEPROM_IMAGE)$(FLASH_IMAGE)$(ELFS)$(LSS)$(S_DEPS)$(SIZEDUMMY)$(S_UPPER_DEPS) pr02-URCHydrophoneTester.elf
	-@echo ' '

secondary-outputs: $(LSS) $(FLASH_IMAGE) $(EEPROM_IMAGE) $(SIZEDUMMY)

.PHONY: all clean dependents
.SECONDARY:

-include ../makefile.targets
