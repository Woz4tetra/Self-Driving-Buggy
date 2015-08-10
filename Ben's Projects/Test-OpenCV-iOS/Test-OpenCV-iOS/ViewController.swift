//
//  ViewController.swift
//  Test-OpenCV-iOS
//
//  Created by Benjamin Warwick on 8/10/15.
//  Copyright (c) 2015 The Ban Hammer. All rights reserved.
//

import UIKit

class ViewController: UIViewController
{
    @IBOutlet var imageView : UIImageView?
    
    override init(nibName nibNameOrNil: String?, bundle nibBundleOrNil: NSBundle?)
    {
        super.init(nibName: nibNameOrNil, bundle: nibBundleOrNil)
        // Custom initialization
    }
    
    required init(coder aDecoder: NSCoder)
    {
        super.init(coder: aDecoder)
    }
    
    override func viewDidLoad()
    {
        super.viewDidLoad()
        
        // Do any additional setup after loading the view.
    }
    
    override func didReceiveMemoryWarning()
    {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    @IBAction func testButton(sender: AnyObject)
    {
//        var image1 = UIImage(named:"pano_19_16_mid.jpg")
//        let imageView:UIImageView = UIImageView.init(image: image1)
//        self.imageView = imageView
//        self.imageView?.image = image1
        CVWrapper.initCameraWithView(imageView)
    }
    
    override func viewDidAppear(animated: Bool)
    {
        super.viewDidAppear(animated)
        
//        var image1 = UIImage(named:"pano_19_16_mid.jpg")
//        let imageView:UIImageView = UIImageView.init(image: image1)
//        print(image1)
//        self.imageView = imageView
//        CVWrapper.initCameraWithView(imageView)
    }
}

