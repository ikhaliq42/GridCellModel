% Create population response movie
path('../include', path);
close all;
clear all;

startTime = 0;
endTime = 8;

dt_track = 0.1;
delta_t = 0.5; % Should be this value.

folder = '../../../simulations/000_test_model/results/';
jobNums = 1000;


nFiles = numel(jobNums);    
for f_it = 1:nFiles
    
    close all;
    clear M;

    jobNums(f_it)
    d = dir([folder 'job' num2str(jobNums(f_it)) '*.mat'])
    if (numel(d) == 0)
        warning(['Could not open job no.' num2str(jobNums(f_it))]);
        continue;
    end
    % Load file which contains the tracking data and extract the spike
    % histogram and blob positions
    d(end).name
    %clear spikeCell
    dataLoad = load([folder d(end).name], 'spikeCell', 'options');       
    spikeCell = dataLoad.spikeCell;
    opts = parseOptions(dataLoad.options);

    disp 'Creating spike histogram';
    spikeHist = createSpikeHistCell(1:numel(spikeCell), spikeCell, ...
        dt_track, 0, endTime);

    figure(2);
    %set(gcf, 'Visible', 'off');

    disp 'Printing frames';
    it = 1;
    for t = startTime:dt_track:endTime
        t
        firingPop = getFiringPop(spikeHist, t, dt_track, delta_t);
        firingPop = reshape(firingPop, opts.sheet_size, opts.sheet_size)';
        image(firingPop, 'Parent', gca);
        title(sprintf('taui = %d', opts.taui));
        xlabel('Neuron no.');
        ylabel('Neuron no.');
        axis equal tight;
        colorbar;

        M(it) = getframe(gcf);

        it = it+1;
    end

    outFile = ['output_local/job' num2str(jobNums(f_it)) '_movie.avi'];
    movie2avi(M, outFile, 'FPS', 10);
    
    clear spikeHist;
end
