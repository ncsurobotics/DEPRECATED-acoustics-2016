from bbb.ADC import ADS7865
from bbb.ADC import ADC_Tools

def adc_config(adc):
    # setup environment
    print("You have entered the ADC config mode")

    # Get user's sample length
    SL = 1e3
    adc.update_sample_length(SL)

    # Get user's conversion rate
    SR = 300e3
    adc.update_sample_rate(eval(SR))

    # Get user's threshold value
    THR = .1
    adc.threshold = eval(THR)

    # Get user's config
    adc.ez_config(0)

    # exit environment
    print("Exiting ADC config mode")
    
def sos_analyzer(adc, ch):
    

def main():
    # Initialize ADC & tools
    adc = ADS7865()
    adc_tools = ADC_Tools()
    
    # Ask user to decide which channel will be used for analysis
    adc.adc_status() # Shows user a list of channels that are available
    channel_sel = eval(
        raw_input("Please enter a channel (0,1,2, or 3) for analysis: ")
    )
    
    # Config the ADC according to taste and ready it for bursting
    adc_config(adc)
    
    # ENTER LOOP FOR ANALYSIS
    while q == 0
    
        # Grab a sample for analysis
        adc.get_data()
        
        # perform analysis
        sos_data = sos_analyzer(adc, channel_sel)
        
        # Let user inspect preview of analysis
        preview_sos_data(adc, ax)
        
        # Let user decide on next course of action
        print("Does the data look suitable?")
        raw_input("enter y/n to confirm or q to quit: ")
        if !preview_good:
            garbage_collect_preview
        else:
            q = 1
            pkg_flg = True
        
    
        
    
    # EXIT LOOP FOR ANALYSIS
    
    # Save data for future usage
    