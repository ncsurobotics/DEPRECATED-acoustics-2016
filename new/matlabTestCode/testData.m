%script for importing acoustics pool data reccorded on osciloscope
filename = 'data/conf1.csv';
outfileyaw = 'processed/conf1yaw.csv';
outfilepitch = 'processed/conf1pitch.csv';
outYaw = fopen(outfileyaw, 'w');
outPitch = fopen(outfilepitch, 'w');
fprintf(outYaw,'index, length, toaCalc, a, b, yaw\n');
fprintf(outPitch, 'index, length, toaCalc, a, b, pitch\n');
data = csvread(filename, 7, 00);
data = data(:, 1:4);
t = 1:length(data);
figure(1)
plot(t, data);
%%
% the frequency of the pinger
pf = 22 * 10^3;
% the frequency of sampling
Fs = 125 * 10^6;
% the number of periods to consider
P = 10;

%figuring out the step size based on pf an Fs something here is wrong
inputSize = Fs/pf * P;
for i = 1:inputSize/2:(length(data) - inputSize)
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
