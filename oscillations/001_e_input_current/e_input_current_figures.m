% Process input current simulation experiment
close all;
clearvars -except results;

%load e_input_current_output_19-Jul-2011;

fontSize = 16;

nParam  = size(results, 1);
nTrials = size(results, 2);

trial_it = 1;
nPar = 31;

dc_ratio = 1/20; % asynchronous mode detection
win_len = 0.002;


t_start = 1.5;
t_end   = 2.5;

for par_it = 1:nPar
    for trial_it = 1:nTrials
        trial_it;
        res = results(par_it, trial_it);
        
        t_start_i = t_start/res.opt.dt + 1;
        t_end_i   = t_end/res.opt.dt + 1;
    
        %firingRate_e = getFiringRate(res.spikeRecord_e(:, t_start_i:t_end_i), res.opt.dt, win_len);
        firingRate_e = res.firingRate_e(t_start_i:t_end_i);
        opt = res.opt;

        
        % Population frequency
%         [Y f NFFT] = fourierTrans(firingRate_e, opt.dt);
%         Y_abs = 2*abs(Y(1:NFFT/2+1));
%         Y_abs = Y_abs.^2;
% 
%         
%         [maxF maxFI] = max(Y_abs);
        %fmax(trial_it, par_it) = getPopOscillationFreq(firingRate_e, dc_ratio, opt.dt);
        fmax(trial_it, par_it) = getPopOscFreqAutoCorr(firingRate_e, opt.dt, 10);

        
        spikeRecord_e = res.spikeRecord_e(:, t_start_i:t_end_i);
        spikeRecord_i = res.spikeRecord_i(:, t_start_i:t_end_i);        
        times = res.times(t_start_i:t_end_i);

        spikeCnt_i = sum(spikeRecord_i');
        
        % mean firing rates of neurons in this trial
        mfr_T = t_end - t_start;

        
        e_mfr_all(:, trial_it, par_it) = full(sum(spikeRecord_e')/mfr_T);
        i_mfr_all(:, trial_it, par_it) = full(sum(spikeRecord_i')/mfr_T);
        e_mfr(trial_it, par_it) = mean(e_mfr_all(:, trial_it, par_it));
        i_mfr(trial_it, par_it) = mean(i_mfr_all(:, trial_it, par_it));
    end
end

nan_fmax = mean(fmax);
nan_fmax(find(isnan(mean(fmax)))) = 0;
nan_fmax(find(nan_fmax > 0)) = nan;

% Print the population and excitatory cells frequency depending on input
% parameter
for par_it = 1:nPar
    Ie(par_it) = results(par_it, 1).opt.Ie;
end

figure('Position', [840 800 800 500]);
subplot(1, 1, 1, 'FontSize', fontSize);
hold on;
plot_h = errorbar([Ie*1000; Ie*1000; Ie*1000]', ...
    [mean(fmax); mean(e_mfr); mean(i_mfr)]', ...
    [std(fmax); std(e_mfr); std(i_mfr)]', ...
    '-o', 'LineWidth', 1);
hold on;
plot(Ie*1000, nan_fmax, '-o', 'LineWidth', 1);

xlabel('Input drive (mV)');
ylabel('Frequency (Hz)');
legend('Oscillation', 'E firing rate', 'I firing rate', 'Location', 'SouthEast');
axis tight;
