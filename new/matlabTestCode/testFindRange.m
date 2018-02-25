% script for importing acoustics pool data reccorded on osciloscope
filename = 'acoustics-data/T1M.csv';
data = csvread(filename, 2, 00);
% Fs is the frequency you want to downsample to
Fdata = 250 * 10^6;
Fs = 250 * 10^6;

%data = downsample(data, Fdata, Fs);
data = data(:, 1:4);
t = 1:length(data);
data(:, 1)=data(:,1);
figure(1)

plot(t, data);
legend({'1', '2', '3', '4'})
%%
% the frequency of sampling
%the frequency of the pinger
pf = 44 * 10^3;

% Figure out how many periods we want to analyze to determine starting
% points
numPeriods = 8;
tPeriod = 1 / pf;
stepSize = round(tPeriod * numPeriods * Fs);
tStart = -1;
% data = downsample(data, Fdata, Fs);
% Zero the center of the data to analyze the start of range
data2 = data - mean(data);
data = data2;

% Figure out where the starting point of the ping is by analyzing the v_rms
% of n periods compared to the total rms up to that point

for i = 1:stepSize:(length(data)-stepSize)
    rms_total = rms(data2(1:i), 2);
    rms_local = rms(data2(i:(i+stepSize)), 2);
    %fprintf("%d-%d, %f, %f\n", i, i+stepSize, rms_total, rms_local);
    if((rms_local > 2 * rms_total) && i > stepSize)
        tStart = i + stepSize;
        break;
    end
    
end



inputSize = round(tPeriod * 10 * Fdata);

% s is the start of the range
s = tStart;
% b is the range to plot/use in fft
b = round(s:(s+inputSize));
figure(2)
p = plot(b, data(b, :));
for i = 1:length(p)
    p(i).LineWidth = 2;
end
legend({'1', '2', '3', '4'});
toa = data(b, :);

%toa(:, [2, 3]) = toa(:, [2, 3]) * -1;
testToa3d(toa, Fs, pf, true);
