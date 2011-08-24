% Pick selected number of sufficiently firing neurons and compute their
% cross correlations
% Interneurons with each other
% Interneurons and principal cells

close all;
clearvars -except results;

path('../include', path);

outputDir = 'output_local';

par_it = 5;
trial_it = 8;

res = results(par_it, trial_it);

mfr_thr = 5;
t_start = 0;
t_end = res.opt.T;

fontSize = 14;


[e_mfr_all i_mfr_all] = meanFiringRateAll(res, t_start, t_end);

% Interneuron - interneuron pairs
i_mfr_thr = find(i_mfr_all > mfr_thr);
i_xcorr_range = 0.15; %s
i_xcorr_dt = 0.001;
i_xcorr_ncells = 10;

for it1 = 1:i_xcorr_ncells
    parfor it2 = 1:i_xcorr_ncells
        [cc edges] = crossCorrelation(res.spikeCell_i{i_mfr_thr(it1)}, res.spikeCell_i{i_mfr_thr(it2)}, i_xcorr_dt, i_xcorr_range, res.opt.T);
        
        figure('Visible','off');
        subplot(1, 1, 1, 'FontSize', fontSize);
        bar(gca, edges*1000, cc, 'histc')
        grid on;
        axis tight;

        xlabel('Time (ms)');
        ylabel('Interval count');

        set(gcf,'PaperPositionMode','auto');
        print('-depsc2', sprintf('%s/003_e_input_spread_i_xcorr_spread_%3.3f_trial_%.3d_cells%d_%d.eps', ...
            outputDir, res.opt.input_spread/res.opt.D, ...
            trial_it, i_mfr_thr(it1), i_mfr_thr(it2)));
    end
end


% Principal cells -interneurons pairs
e_mfr_thr = find(e_mfr_all > mfr_thr);
ei_xcorr_range = 0.1; %s
ei_xcorr_dt = 0.001;
ei_xcorr_ncells = 10;

for it1 = 1:ei_xcorr_ncells
    parfor it2 = 1:ei_xcorr_ncells
        [cc edges] = crossCorrelation(res.spikeCell_e{e_mfr_thr(it1)}, res.spikeCell_i{i_mfr_thr(it2)}, ei_xcorr_dt, ei_xcorr_range, res.opt.T);
        
        figure('Visible','off');
        subplot(1, 1, 1, 'FontSize', fontSize);
        bar(gca, edges*1000, cc, 'histc')
        grid on;
        axis tight;

        xlabel('Time (ms)');
        ylabel('Interval count');

        set(gcf,'PaperPositionMode','auto');
        print('-depsc2', sprintf('%s/003_e_input_spread_ei_xcorr_spread_%3.3f_trial_%.3d_cells%d_%d.eps', ...
            outputDir, res.opt.input_spread/res.opt.D, ...
            trial_it, e_mfr_thr(it1), i_mfr_thr(it2)));
    end
end


% Principal cells -interneurons pairs
e_mfr_thr = find(e_mfr_all > mfr_thr);
ee_xcorr_range = 0.15; %s
ee_xcorr_dt = 0.001;
ee_xcorr_ncells = 10;

for it1 = 1:ee_xcorr_ncells
    parfor it2 = 1:ee_xcorr_ncells
        [cc edges] = crossCorrelation(res.spikeCell_e{e_mfr_thr(it1)}, res.spikeCell_e{e_mfr_thr(it2)}, ee_xcorr_dt, ee_xcorr_range, res.opt.T);
        
        figure('Visible','off');
        subplot(1, 1, 1, 'FontSize', fontSize);
        bar(gca, edges*1000, cc, 'histc')
        grid on;
        axis tight;

        xlabel('Time (ms)');
        ylabel('Interval count');

        set(gcf,'PaperPositionMode','auto');
        print('-depsc2', sprintf('%s/003_e_input_spread_ee_xcorr_spread_%3.3f_trial_%.3d_cells%d_%d.eps', ...
            outputDir, res.opt.input_spread/res.opt.D, ...
            trial_it, e_mfr_thr(it1), e_mfr_thr(it2)));
    end
end