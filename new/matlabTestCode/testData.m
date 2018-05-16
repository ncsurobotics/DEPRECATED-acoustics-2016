%script for importing acoustics pool data reccorded on osciloscope
filename = '/home/rafael/Downloads/data.csv';
outfileyaw = 'yaw.csv';
outfilepitch = 'pitch.csv';
outYaw = fopen(outfileyaw, 'w');
outPitch = fopen(outfilepitch, 'w');
fprintf(outYaw,'index, length, toaCalc, a, b, yaw\n');
fprintf(outPitch, 'index, length, toaCalc, a, b, pitch\n');
freq = csvread(filename, 00, 00, [00, 00, 00, 0]);
data = csvread(filename, 2, 00);
%time = data(:, 1);
%data = data(:, 2:end);
t = 1:length(data);
figure(1)
plot(t, data);
%%
% the frequency of the pinger
pf = 22 * 10^3;
% the frequency of sampling
%plot(abs(time(2:end) - time(1:end - 1)), 'o')
%tDiff = mean(abs(time(2:end) - time(1:end - 1))) * 10^-3;
Fs = freq; %1/tDiff;
%%

% the number of periods to consider
P = 15;

inputSize = Fs/pf * P;
for i = 1:inputSize/4:(length(data) - inputSize)
    t = uint64(i:1:(i + inputSize));
    toa = data(t, :);
    %figure(2)
    %plot(toa)
    out = testToa3d(toa, Fs, pf, false);
    fprintf(outYaw, '%d, %s', uint64(i), out{1});
    fprintf(outPitch,'%d, %s', uint64(i), out{2});
end
fclose(outYaw);
fclose(outPitch);
