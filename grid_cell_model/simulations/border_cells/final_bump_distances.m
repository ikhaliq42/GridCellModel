cell_counts  = [0 1 2 3 4 5 6 7 8 9 10];
trial_nums = [0 1 2 3 4 5 6 7];
start_distances  = [5 10 15 20 5 10 15 20];
plot_colours = ['c','g','r','b','k','m','y'];

final_distances = zeros(size(cell_counts,2),size(trial_nums,2));
for cell_count_idx = 1:size(final_distances,1)
    for trial_idx = 1:size(final_distances,2)
        
        %read data
        nCells = cell_counts(cell_count_idx); 
        trial_no = trial_nums(trial_idx);
        path = sprintf('sim_bump_test_%i_cells/150pA/',nCells);
        filename = sprintf('BumpParams_trial%i.mat',trial_no);
        h5filename = 'job00000_output.h5';
        load(strcat(path,filename));

        % get distances
        targ_y = 15; targ_x = 17;
        dist_y = abs(params.mu_y - targ_y);
        dist_x = abs(params.mu_x - targ_x); 
        dist = sqrt(dist_x .^2 + dist_y .^2);
        final_distances(cell_count_idx,trial_idx) = dist(4501);
       
    end
end

%draw plots
s=1;e=4;
bar3(final_distances(:,s:e));
set(gca, 'YTickLabel',cell_counts, 'YTick',1:numel(cell_counts))
set(gca, 'XTickLabel',start_distances(s:e), 'XTick',1:numel(start_distances(s:e)))
title('Final bump distance to target');
xlabel('Start Distance (cm)'); ylabel('Number of border cells'); zlabel('Final Distance(neurons)');

