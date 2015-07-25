cell_counts  = [0 2 4 6 8 10];
plot_colours = ['c','g','r','b','k','m','y'];
handles = [];
hold on;
trial_no = 1; 

for idx = 1:size(cell_counts,2)
    nCells = cell_counts(idx); 
    path = sprintf('sim_bump_test_%i_cells/150pA/',nCells);

    filename = sprintf('BumpParams_trial%i.mat',trial_no);
    h5filename = 'job00000_output.h5';
    load(strcat(path,filename));

    % distances
    targ_y = 15; targ_x = 17;
    dist_y = abs(params.mu_y - targ_y);
    dist_x = abs(params.mu_x - targ_x);
    dist = sqrt(dist_x .^2 + dist_y .^2);  
    
    % draw plot
    handles = [handles plot(dist,plot_colours(idx))];
    axis([1000 4500 0 15]);
    title('Bump distance to target');
    xlabel('Time (ms)'); ylabel('Distance (neurons)');
    label = sprintf('%i cells', nCells);
    legend(handles(idx),sprintf('%i cells',nCells));
end


legend('location','NE')
hold off;