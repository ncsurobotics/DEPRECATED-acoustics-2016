function downsampled = downsample(data, srcSample, targetSample)
step = srcSample / targetSample;
downsampled = data(1:step:end,:);
end
