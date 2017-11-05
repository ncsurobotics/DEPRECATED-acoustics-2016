% script for importing acoustics pool data reccorded on osciloscope
filename = 'acoustics-data/conf2.csv';
data = csvread(filename, 7, 00);
data = data(:, 1:4);
t = 1:length(data);
plot(t, data);
%%

% the frequency of sampling
Fs = 125 * 10^6;
%the frequency of the pinger
pf = 22 * 10^3;
% the starting point of the input
i= 2.5 * 10^5;
%size of the input
numPeriods = 8;
tPeriod = 1 / pf;
inputSize = round(tPeriod * numPeriods * Fs);
tStart = -1;
for i = 1:inputSize:length(data)
    rms_total = rms(data(1:i));
    rms_local = rms(data(i:(i+inputSize)));
    if((rms_local > 5 * rms_total) && i > inputSize)
        tStart = i + inputSize * 2;
        break;
    end
    
end

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
