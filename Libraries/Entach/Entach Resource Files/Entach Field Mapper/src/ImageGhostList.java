
import java.awt.*;
import java.awt.geom.AffineTransform;
import java.util.ArrayList;

public class ImageGhostList
{
	private ArrayList<ImageGhost> imageGhostList = new ArrayList<ImageGhost>();
	
	public ImageGhostList()
	{
		
	}
	
	public void addImageGhost(ImageGhost newImageGhost)
	{
		imageGhostList.add(newImageGhost);
	}
	
	public void removeImageGhost(int index)
	{
		imageGhostList.remove(index);
	}
	
	public ImageGhost getImageGhost(int index)
	{
		return imageGhostList.get(index);
	}
	
	public int getListSize()
	{
		return imageGhostList.size();
	}
	
	public void redrawImageGhosts(Graphics g, Image robotImage, double scaleX, double scaleY)
	{	
		for (int index = 0; index < imageGhostList.size(); index++)
		{
			if (imageGhostList.get(index).getIsHidden() == false)
			{
				Graphics2D g2 = (Graphics2D) g;
				AffineTransform image = new AffineTransform();
				image.translate(imageGhostList.get(index).getImageLocationX(), imageGhostList.get(index).getImageLocationY());
				image.rotate(Math.toRadians((360 - imageGhostList.get(index).getImageAngle()) + 90), imageGhostList.get(index).getImageWidth() / 2, imageGhostList.get(index).getImageHeight() / 2);
				image.scale(scaleX, scaleY);
				
				g2.drawImage(robotImage, image, null);
			}
			g.setColor(Color.WHITE);
			g.drawString("" + (index), (int) imageGhostList.get(index).getImageLocationX() + imageGhostList.get(index).getImageWidth() / 2 - 3, (int) imageGhostList.get(index).getImageLocationY() + imageGhostList.get(index).getImageHeight() / 2 + 4);
			g.setColor(Color.GREEN);
		}
	}
	
	public void printAngles(Graphics g)
	{
		g.drawString("End Angle",720,20);
		for (int index = 0; index < imageGhostList.size(); index++)
			imageGhostList.get(index).printContent(g, (index + 1) * 15);
	}
	
	public void removeAllImageGhosts()
	{
		for (int index = 0; index < imageGhostList.size(); index++)
		{
			imageGhostList.remove(index);
			index--;
		}
	}

	public ArrayList<ImageGhost> getArrayList()
	{
		return imageGhostList;
	}
}
