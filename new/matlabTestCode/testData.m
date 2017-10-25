%script for importing acoustics pool data reccorded on osciloscope
filename = 'data/conf2.csv';
data = csvread(filename, 7, 00);
data = data(:, 1:4);
t = 1:length(data);
plot(t, data);
%%
% s is the start of the range
s = (2.5* 10^5);
% b is the range to plot/use in fft
b = round(s:(s+(50 * 10^3)));
figure(2)
p = plot(b, data(b, :));
for i = 1:length(p)
    p(i).LineWidth = 2;
end
legend({'1', '2', '3', '4'});
toa = data(b, :);

%toa(:, [2, 3]) = toa(:, [2, 3]) * -1;
testToa3d(toa)
