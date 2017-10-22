function calcToa = signalToa(sig1, sig2, ch1, ch2)
%% making the time axis

% % frequency values are read in at in hz
Fs = 125 * 10^6;
% % number of values read in
L = length(sig1);
if L/2 ~= round(L/2)
    L = L-1;
    sig1 = sig1(1:L);
    sig2 = sig2(1:L);
end
% % period of read in values 
% T = 1/(Fs);
% % time axis 
% t = (0:M-1) * T;
% %% making the y axis, acoustic wave read in
% % frequency of wave from ping in hz
pf = 22* 10^3;
% 
% % the input read in from the hydrophone, assuming 0 offset
% signal = [cos(2 * pi * ( pf) * t); cos(2 * pi * pf * (t + toa))];
%% plotting the output wave
figure()
t = 1:length(sig1);
plot(t, sig1, t, sig2);
t = sprintf('plot of signal %s and %s', ch1, ch2);
title(t)
ylabel('amplitude of sign')
xlabel('time in secconds')
legend({ch1, ch2})
%%
Y = [fft(sig1');fft(sig2')];
P2 = abs(Y/L);
P1 = P2(:, 1:L/2 + 1);
P1(2:end - 1, :) = 2 * P1(2:end - 1, :);
f = Fs * (0:L/2)/L;
range = f > (15 * 10^3) & f < 27 * 10^3;
figure()
plot(f(range), P1(1, range), f(range), P1(2, range));
title('fft');
legend({ch1, ch2})
Y = Y(:, range);
[~,i] = max(abs(Y'));
calcToa = (angle(Y(2, i(2))) - angle(Y(1, i(1))))/(pf * 2 * pi); 
end


