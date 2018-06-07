clc
clear
%%
tolerance = 13;
step = 5;
depth = -2;
radius = 6;



for deg = int64(0:step:360)
    y = radius * cosd(double(deg));
    x = radius * sind(double(deg));
    
    try
        result = toaSimulation( x, y, depth );
        if result.yaw < -.1
           yaw = result.yaw + 360;
        else
            yaw = result.yaw;
        end
        
       
        if (abs(yaw - deg) > tolerance) 
            fprintf("ERROR at yaw: %5.2f\n", deg);
            fprintf("x: %5.3f\ty: %5.3f\n", x, y);
            
            fprintf("Calculated yaw: %5.2f\n", result.yaw);
            fprintf("-------------------------------------\n");
        end
    catch ME
        fprintf("ERROR at yaw: %5.2f\n", deg);
        fprintf("x: %5.3f\ty: %5.3f\n", x, y);
        fprintf("exception during calculation\n");
        fprintf("%s\n", ME.message);
        fprintf("%s\n", getReport(ME));
        fprintf("-------------------------------------\n");
       
        
    end
end

            