set(gcf,'Visible','off');

for exp_no = 0:7; 

    fprintf('Generating plot for experiment %i...\n', exp_no);
    cell_counts  = [0 2 4 6 8 10];
    plot_colours = ['c','g','r','b','k','m','y'];
    targ_y = 15; targ_x = 17;
    handles = [];
            
    for idx = 1:size(cell_counts,2)
    
        nCells = cell_counts(idx); 
        path = sprintf('sim_bump_test_%i_cells/experiment_%i/',nCells,exp_no);
        
        dists = [];
        
        for trial_no = 0:9

            filename = sprintf('BumpParams_trial%i.mat',trial_no);
            load(strcat(path,filename));

            % distances
            dist_y = abs(params.mu_y - targ_y);
            dist_x = abs(params.mu_x - targ_x);
            dists = [dists; sqrt(dist_x .^2 + dist_y .^2)]; 
            
        end
        
        dist = mean(dists,1);
        
        % draw plot
        handles = [handles plot(dist,plot_colours(idx))];		
        hold on;
        axis([1000 4500 0 15]);
        title('Bump distance to target');
        xlabel('Time (ms)'); ylabel('Distance (neurons)');
        label = sprintf('%i cells', nCells);
        legend(handles(idx),sprintf('%i cells',nCells));
        
    end
    
    legend('location','NE')
    fprintf('Saving plot for experiment %i...\n', exp_no);
	saveas(gcf,sprintf('bump_dists_exp_%i',exp_no),'fig');
    
    %pause();
    hold off;
    clear; 

end


