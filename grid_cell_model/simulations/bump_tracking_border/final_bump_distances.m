set(gcf,'Visible','off');
cell_counts  = [0 1 2 3 4 5 6 7 8 9 10];
exp_nums = [0 1 2 3 4 5 6 7];
start_distances  = [5 10 15 20 5 10 15 20];
plot_colours = ['c','g','r','b','k','m','y'];
targ_y = 15; targ_x = 17; end_time = 4501;
ntrials = 10;

final_distances = zeros(size(cell_counts,2),size(exp_nums,2));
for cell_count_idx = 1:size(cell_counts,1)
    for exp_idx = 1:size(exp_nums,2)
	
	    %read data
		nCells = cell_counts(cell_count_idx); 
		exp_no = exp_nums(exp_idx);
		path = sprintf('sim_bump_test_%i_cells/experiment_%i/',nCells,exp_no);
		fin_dist = zeros(1,10);
	
		for trial_idx = 1:ntrials
		    
            fprintf('Generating plot: cell count %i, experiment %i, trial %i...\n', nCells, exp_no, trial_idx-1);
			filename = sprintf('BumpParams_trial%i.mat',trial_idx-1);
			load(strcat(path,filename));

			% get distances
			dist_y = abs(params.mu_y(end_time) - targ_y);
			dist_x = abs(params.mu_x(end_time) - targ_x); 
			dist = sqrt(dist_x .^2 + dist_y .^2);
			fin_dist(trial_idx) = dist;
		   
		end
		
		final_distances(cell_count_idx,trial_idx) = mean(fin_dist);
		
	end
end

%draw plots
s=1;e=4;
bar3(final_distances(:,s:e));
set(gca, 'YTickLabel',cell_counts, 'YTick',1:numel(cell_counts))
set(gca, 'XTickLabel',start_distances(s:e), 'XTick',1:numel(start_distances(s:e)))
title('Final bump distance to target');
xlabel('Start Distance (cm)'); ylabel('Number of border cells'); zlabel('Final Distance(neurons)');

fprintf('Saving plot...\n');
print('final_bump_dists','-dpng');
