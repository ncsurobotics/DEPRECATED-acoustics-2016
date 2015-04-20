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
LTC1564_Tester.lss \

FLASH_IMAGE += \
LTC1564_Tester.hex \

EEPROM_IMAGE += \
LTC1564_Tester.eep \

SIZEDUMMY += \
sizedummy \


# All Target
all: LTC1564_Tester.elf secondary-outputs

# Tool invocations
LTC1564_Tester.elf: $(OBJS) $(USER_OBJS)
	@echo 'Building target: $@'
	@echo 'Invoking: AVR C Linker'
	avr-gcc -Wl,-Map,LTC1564_Tester.map -mmcu=atmega328p -o "LTC1564_Tester.elf" $(OBJS) $(USER_OBJS) $(LIBS)
	@echo 'Finished building target: $@'
	@echo ' '

LTC1564_Tester.lss: LTC1564_Tester.elf
	@echo 'Invoking: AVR Create Extended Listing'
	-avr-objdump -h -S LTC1564_Tester.elf  >"LTC1564_Tester.lss"
	@echo 'Finished building: $@'
	@echo ' '

LTC1564_Tester.hex: LTC1564_Tester.elf
	@echo 'Create Flash image (ihex format)'
	-avr-objcopy -R .eeprom -R .fuse -R .lock -R .signature -O ihex LTC1564_Tester.elf  "LTC1564_Tester.hex"
	@echo 'Finished building: $@'
	@echo ' '

LTC1564_Tester.eep: LTC1564_Tester.elf
	@echo 'Create eeprom image (ihex format)'
	-avr-objcopy -j .eeprom --no-change-warnings --change-section-lma .eeprom=0 -O ihex LTC1564_Tester.elf  "LTC1564_Tester.eep"
	@echo 'Finished building: $@'
	@echo ' '

sizedummy: LTC1564_Tester.elf
	@echo 'Invoking: Print Size'
	-avr-size --format=avr --mcu=atmega328p LTC1564_Tester.elf
	@echo 'Finished building: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) $(OBJS)$(C_DEPS)$(ASM_DEPS)$(EEPROM_IMAGE)$(FLASH_IMAGE)$(ELFS)$(LSS)$(S_DEPS)$(SIZEDUMMY)$(S_UPPER_DEPS) LTC1564_Tester.elf
	-@echo ' '

secondary-outputs: $(LSS) $(FLASH_IMAGE) $(EEPROM_IMAGE) $(SIZEDUMMY)

.PHONY: all clean dependents
.SECONDARY:

-include ../makefile.targets
