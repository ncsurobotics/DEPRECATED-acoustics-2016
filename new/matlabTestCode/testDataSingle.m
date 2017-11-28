filename = '/home/rafael/Documents/Robotics Documentation/acoustics/data/conf1.csv';
data = csvread(filename, 7, 00);
data = data(:, 1:4);
t = 1:length(data);
figure(1)
plot(t, data);
%%
% the frequency of sampling
Fs = 1 * 10^6;
%the frequency of the pinger
pf = 22 * 10^3;
% the starting point of the input
i= 2.5 * 10^5;
%size of the input
inputSize = 5*10^4;

t = uint64(i:1:(i + inputSize));
toa = data(t, :);
figure(2)
plot(toa)
out = testToa3d(toa, Fs, pf, true);
fprintf('length, toaCalc, a, b, yaw\n');
fprintf(out{1});
fprintf('length, toaCalc, a, b, pitch\n');
fprintf(out{2});

