function [] = extract_bump_data(cells_per, experiment) 
% code to extract the bump mu and sigma values for a reduced size data file

    for trial_no = 0:9 
        
        path = sprintf('sim_bump_test_%i_cells/experiment_%i/',cells_per,experiment);
        filename = sprintf('BumpParams_trial%i.mat',trial_no);
        h5filename = 'job00000_output.h5';
        fprintf(strcat('loading data... ', path, filename,'\n'));
        load(strcat(path,filename));

        if cells_per > 0 
            h5dataPath = sprintf('/trials/%i/connections/B->E',trial_no);
            conns = h5read(strcat(path,h5filename),h5dataPath);				
            border = conns; %reshape(conns(1,:),34,30)';
        end

        fprintf('extracting...\n');
        mu_x = params.mu_x;
        mu_y = params.mu_y;
        sigma = params.sigma;

        output_path = 'bump_data_reduced/';
        output_file = sprintf('bump_pos_bc_%i_exp_%i_trial_%i', cells_per, experiment, trial_no);			
        fprintf(strcat('Saving data... ', output_path, output_file, '\n'));
		
		if cells_per > 0 
			save(strcat(output_path, output_file),'mu_x','mu_y','sigma','border');
		else
			save(strcat(output_path, output_file),'mu_x','mu_y','sigma');		
		end

	end
end
