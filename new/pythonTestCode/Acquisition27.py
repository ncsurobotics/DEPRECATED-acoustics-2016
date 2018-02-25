--- AnalogIn_Acquisition.py	(original)
+++ AnalogIn_Acquisition.py	(refactored)
@@ -29,20 +29,20 @@
 #print DWF version
 version = create_string_buffer(16)
 dwf.FDwfGetVersion(version)
-print "DWF Version: "+version.value
+print("DWF Version: "+version.value)
 
 #open device
-print "Opening first device"
+print("Opening first device")
 dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
 
 if hdwf.value == hdwfNone.value:
     szerr = create_string_buffer(512)
     dwf.FDwfGetLastErrorMsg(szerr)
-    print szerr.value
-    print "failed to open device"
+    print(szerr.value)
+    print("failed to open device")
     quit()
 
-print "Preparing to read sample..."
+print("Preparing to read sample...")
 
 #set up acquisition
 dwf.FDwfAnalogInFrequencySet(hdwf, c_double(20000000.0))
@@ -55,22 +55,22 @@
 
 #begin acquisition
 dwf.FDwfAnalogInConfigure(hdwf, c_bool(False), c_bool(True))
-print "   waiting to finish"
+print("   waiting to finish")
 
 while True:
     dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
-    print "STS VAL: " + str(sts.value) + "STS DONE: " + str(DwfStateDone.value)
+    print("STS VAL: " + str(sts.value) + "STS DONE: " + str(DwfStateDone.value))
     if sts.value == DwfStateDone.value :
         break
     time.sleep(0.1)
-print "Acquisition finished"
+print("Acquisition finished")
 
 dwf.FDwfAnalogInStatusData(hdwf, 0, rgdSamples, 4000)
 dwf.FDwfDeviceCloseAll()
 
 #plot window
 dc = sum(rgdSamples)/len(rgdSamples)
-print "DC: "+str(dc)+"V"
+print("DC: "+str(dc)+"V")
 
 rgpy=[0.0]*len(rgdSamples)
 for i in range(0,len(rgpy)):
