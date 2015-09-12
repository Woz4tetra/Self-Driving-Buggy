
import java.awt.Graphics;

public class ImageGhost
{
	private String imageName;
	private int xPosition = 0, yPosition = 0, imageAngle = 0;
	private int imageWidth, imageHeight;
	private boolean isHidden = false;
	
	public ImageGhost(String inputName, int x, int y, int inputAngle, int width, int height)
	{
		imageName = inputName;
		xPosition = x;
		yPosition = y;
		imageAngle = inputAngle;
		
		imageWidth = width;
		imageHeight = height;
	}
	
	public String getImageName() { return imageName; }
	public int getImageLocationX() { return xPosition; }
	public int getImageLocationY() { return yPosition; }
	public int getImageAngle() { return imageAngle; }
	public int getImageWidth() { return imageWidth; }
	public int getImageHeight() { return imageHeight; }
	
	public boolean getIsHidden() { return isHidden; }
	public void setIsHidden(boolean hide) { isHidden = hide; }
	public void toggleIsHidden()
	{
		if (isHidden == true)
			isHidden = false;
		else
			isHidden = true;
	}
	
	public void printContent(Graphics g, int inputX)
	{
		g.drawString("" + imageAngle,720,20 + inputX);
	}
}
