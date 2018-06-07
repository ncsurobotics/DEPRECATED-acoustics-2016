function calcToa = signalToa2(toa)
%% making the time axis

% frequency values are read in at in hz
Fs = 1000 * 10^3;
% number of values read in
M = 1000;
% period of read in values 
T = 1/(Fs);
% time axis 
t = (0:(2*M)-1) * T;
%% making the y axis, acoustic wave read in
% frequency of wave from ping in ohz
pf = 22* 10^3;
offset = round(toa/T);
index = M * 0.5;
index2 = round(index + offset);
t1 = t(index:(M+index));
t2 = t(index2:(M+index2));

% the input read in from the hydrophone, assuming 0 offset
signal = [cos(2 * pi * ( pf) * t1); cos(2 * pi * pf * t2)];
%% plotting the output wave
%{
figure()
hold on
plot(signal(1,:))
plot(signal(2,:));
hold off
title('plot of signal')
ylabel('amplitude of sign')
xlabel('time in secconds') 
%}
%%
Y = [fft(signal(1,:));fft(signal(2,:))];
[~,i] = max(abs(Y'));
Y(2, i(2));
Y(1, i(1));
calcToa = (angle(Y(2, i(2))) - angle(Y(1, i(1))))/(pf * 2 * pi);
%x = 8;
%calcToa = round(toa * 10^x) * 10^(-1 * x);% + toa * err;
%err = ((-1)^randi([1,2])) * .05;
%calcToa = toa + toa*err;
%err = %abs(toa - calcToa)/toa;
err = 0;

%fprintf('IN: %6.2f TDOA: %6.2f, TDOA error: %6.2f%%\n', toa * 10^5, calcToa * 10^5, err * 100);
end


