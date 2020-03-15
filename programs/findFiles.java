package programs;

import java.io.File;
import java.io.IOException;

public class findFiles {
    public static void main(String[] args) throws IOException {
        File path = new File("C:/Users/Zach/Documents/Github/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports");
    
        File [] files = path.listFiles();

        int count = 0;
    
        for (int i = 0; i < files.length; i++){
            if (files[i].isFile()){ //this line weeds out other directories/folders
                count = count + 1;
                
                File fileName = files[i];
                String absolutePath = fileName.getAbsolutePath();

                int length = absolutePath.length();

                String filePath = absolutePath.substring(absolutePath.lastIndexOf(File.separator) + 1, length - 4);

                if (filePath.length() == 10) {
                    if (count == files.length - 2) {
                        System.out.println(filePath);
                    }
                }
                else {
                    i++;
                }
            }
        }
    }
}
