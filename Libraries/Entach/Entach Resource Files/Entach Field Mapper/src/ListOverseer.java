
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.util.Calendar;
import javax.imageio.ImageIO;
import javax.swing.JPanel;

public class ListOverseer
{
	CoordinateList goToPoints = new CoordinateList();
	CheckBoxList CheckBoxes = new CheckBoxList();
	ImageGhostList imageGhosts = new ImageGhostList();
	
	Dimension screenSize;
	Point screenLocation;
	
	public ListOverseer(CoordinateList inputGoToPoints, CheckBoxList inputCheckBoxes, ImageGhostList inputImageGhosts, JPanel panel)
	{
		goToPoints = inputGoToPoints;
		CheckBoxes = inputCheckBoxes;
		imageGhosts = inputImageGhosts;
		
		screenSize = panel.getSize();
		screenLocation = panel.getLocation();
	}
	
	public void writePointsToFile(int fieldImageHeight) throws Exception
	{	
		String AM_PM;
		if (Calendar.getInstance().get(Calendar.AM_PM) == 0)
			AM_PM = "AM";
		else
			AM_PM = "PM";
		
		String currentTime = (Calendar.getInstance().get(Calendar.MONTH) + 1) + "-" + Calendar.getInstance().get(Calendar.DAY_OF_MONTH) + "-" + Calendar.getInstance().get(Calendar.YEAR) + " " + Calendar.getInstance().get(Calendar.HOUR) + "h " + Calendar.getInstance().get(Calendar.MINUTE) + "m " + Calendar.getInstance().get(Calendar.SECOND) + "s " + AM_PM;
		
		captureScreen("Outputs/goToPoint " + currentTime + "/", "goToPoints Image " + currentTime);
		
		FileWriter goToPointsLog = new FileWriter("Outputs/goToPoint " + currentTime + "/goToPoints Log " + currentTime + ".txt");
		
		BufferedWriter outStream = new BufferedWriter(goToPointsLog);
		
		Coordinate coordToAnalyze = goToPoints.getCoordinate(0);
		outStream.write("//File name: \"goToPoints Log " + currentTime + ".txt\"\n");
		outStream.write("initializeAxes(" + coordToAnalyze.convertCoordinate(coordToAnalyze.getX()) + ", " + coordToAnalyze.convertCoordinate((fieldImageHeight - coordToAnalyze.getY())) + ", " + Math.toRadians(imageGhosts.getImageGhost(0).getImageAngle()) + "); // Point #0" + "\n\n");
		
		for (int index = 1; index < goToPoints.getListSize(); index++)
		{
			String outString;
			coordToAnalyze = goToPoints.getCoordinate(index);
			
			double xCoordinate = coordToAnalyze.convertCoordinate(coordToAnalyze.getX());
			double yCoordinate = coordToAnalyze.convertCoordinate((fieldImageHeight - coordToAnalyze.getY()));
			
			if (CheckBoxes.getArrayList().get(index).getIsChecked() == true)
				outString = "goToPoint(" + xCoordinate + ", " + yCoordinate + ", " + Math.toRadians(imageGhosts.getImageGhost(index).getImageAngle()) + "); // Point #" + (index) + "\n";
			else
				outString = "goToPoint(" + xCoordinate + ", " + yCoordinate + "); // Point #" + (index) + "\n";
			outStream.write(outString);
		}
		outStream.close();
	}
	
	public void captureScreen(String filePath, String fileName) throws Exception
	{
	   Dimension screenSize = new Dimension(904, 432 + 50 + 290);//Toolkit.getDefaultToolkit().getScreenSize();
	   Rectangle screenRectangle = new Rectangle(new Point(0, 44), screenSize);
	   Robot robot = new Robot();
	   BufferedImage image = robot.createScreenCapture(screenRectangle);
	   
	   try {
		   new File(filePath).mkdirs();
	   }
	   catch(SecurityException se){	}
	   
	   ImageIO.write(image, "png", new File(filePath + fileName));
	}
	
	public void deleteAllPaths(JPanel panel)
	{
		if(goToPoints.getListSize() != 0)
			while (goToPoints.getListSize() >= 1)
				goToPoints.removeCoordinate(goToPoints.getListSize() - 1);
		if(imageGhosts.getListSize() != 0)
			while (imageGhosts.getArrayList().size() >= 1)
				imageGhosts.getArrayList().remove(imageGhosts.getArrayList().size() - 1);
		if(CheckBoxes.getListSize() != 0)
			CheckBoxes.removeAllCheckBoxes(panel);
	}
	
	public void deleteLastPath(JPanel panel)
	{
		if (goToPoints.getListSize() > 0)
			goToPoints.removeCoordinate(goToPoints.getListSize() - 1);
		if (imageGhosts.getArrayList().size() > 0)
			imageGhosts.getArrayList().remove(imageGhosts.getArrayList().size() - 1);
		if (CheckBoxes.getArrayList().size() > 1)
			CheckBoxes.removeCheckBox(CheckBoxes.getArrayList().size() - 1, panel);
	}
	
	public void submitResults(int fieldImageHeight, JPanel panel)
	{
		if (goToPoints.getListSize() > 0 && imageGhosts.getListSize() > 0 && CheckBoxes.getListSize() > 0)
		{
			try { writePointsToFile(fieldImageHeight); }
			catch (IOException e1) { e1.printStackTrace(); }
			catch (Exception e1) { e1.printStackTrace(); }
			
			deleteAllPaths(panel);
		}
	}
}
