import datetime
import omni.replicator.core as rep

basepath = "c:\\Users\\adam\\Desktop\\Omniverse\\Src"
dataset = "Apple"
output_dir = basepath+'\\data\\rendered\\'+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+'\\'+dataset

with rep.new_layer():

    TABLE_ASSET = "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/ArchVis/Residential/Furniture/DiningSets/EastRural/EastRural_Table.usd"
    FRUIT = {
        "Apple":  "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/ArchVis/Residential/Food/Fruit/Apple.usd",
        "Orange":"http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/ArchVis/Residential/Decor/Tchotchkes/Orange_01.usd",
        "Lime": "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/ArchVis/Residential/Food/Fruit/Lime01.usd"
    }
    
    def table():
        table = rep.create.from_usd(
            TABLE_ASSET, semantics=[('class', 'table')])

        with table:
            rep.physics.collider()
            rep.physics.mass(mass=100)
            rep.modify.pose(
                position=(0, 0, 0),
                rotation=(0, -90, -90),
            )
        return table
        
    rep.randomizer.register(table)

    def rect_lights(num=1):
        lights = rep.create.light(
            light_type="rect",
            temperature=rep.distribution.normal(5500, 500),
            intensity=rep.distribution.normal(0, 50),
            position=(0, 250, 0),
            rotation=(-90, 0, 0),
            count=num
        )
        return lights.node

    rep.randomizer.register(rect_lights)

    def dome_lights(num=1):
        lights = rep.create.light(
            light_type="dome",
            temperature=rep.distribution.normal(5500, 500),
            intensity=rep.distribution.normal(0, 100),
            position=(0, 200, 18),
            rotation=(225, 0, 0),
            count=num
        )
        return lights.node

    rep.randomizer.register(dome_lights)
    
    def randomize_asset(fpath, fclass, maxnum = 1):
        instances = rep.randomizer.instantiate(
            fpath, size=maxnum, mode='scene_instance')
        with instances:
            rep.physics.collider()
            rep.physics.mass(mass=100)
            rep.modify.semantics([('class', fclass)])
            rep.modify.pose(
                position=rep.distribution.uniform(
                    (-15, 90, -15), (20, 90, 20)),
                rotation=rep.distribution.uniform(
                    (-90, -180, -90), (90, 180, 90)),
                scale=rep.distribution.uniform((2.5),(3.5)),
            )
        return instances.node
       
    rep.randomizer.register(randomize_asset)
    
    camera = rep.create.camera(
        focus_distance=90, focal_length=35,
        position=(0, 285, 0), rotation=(-90, 0, 0), f_stop=16)
    render_product = rep.create.render_product(camera, (512, 512))
    
    # FOR LIMES
    #camera = rep.create.camera(
    #    focus_distance=90, focal_length=35,
    #   position=(0, 300, 0), rotation=(-90, 0, 0), f_stop=16)
    #render_product = rep.create.render_product(camera, (512, 512))
    
    camera2 = rep.create.camera(
        focus_distance=90, focal_length=30,
        position=(0, 275, 0), rotation=(-85, 0, 0), f_stop=16)
    render_product2 = rep.create.render_product(camera2, (512, 512))
                
    writer = rep.WriterRegistry.get("BasicWriter")
    writer.initialize(
        output_dir = output_dir, 
        rgb=True, bounding_box_2d_tight=True)
    writer.attach([render_product, render_product2])

    with rep.trigger.on_frame(num_frames=75):
        # Table
        rep.randomizer.table()
        # Lights
        rep.randomizer.rect_lights(1)
        rep.randomizer.dome_lights(1)
        # Fruit
        if dataset == "None":
            pass
        elif dataset == "All":
            for fclass, fpath in FRUIT.items():
                rep.randomizer.randomize_asset(fpath, fclass, 1)
        else:
            rep.randomizer.randomize_asset(FRUIT[dataset], dataset, 1)
    
    rep.orchestrator.run()